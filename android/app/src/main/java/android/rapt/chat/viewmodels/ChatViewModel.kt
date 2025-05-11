package android.rapt.chat.viewmodels

import android.rapt.chat.models.ChatObj
import android.rapt.chat.models.Contact
import android.rapt.chat.models.MessageType
import android.rapt.chat.models.SocketMessage
import android.rapt.chat.models.toDBChat
import android.rapt.chat.repositories.ChatRepository
import android.rapt.chat.sources.ChatRoomDao
import android.rapt.chat.sources.ContactDao
import android.rapt.chat.sources.DBChat
import android.rapt.chat.sources.DBChatRoom
import android.rapt.chat.sources.DBContact
import android.rapt.chat.sources.toSocketMessage
import android.util.Log
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharedFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asSharedFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.collectLatest
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import retrofit2.HttpException
import java.io.IOException
import javax.inject.Inject

sealed class ConnectionStatus {
    data object Connected : ConnectionStatus()
    data object Reconnecting : ConnectionStatus()
    data object Disconnected : ConnectionStatus()
}

data class ChatState(
    val isLoading: Boolean = false,
    val error: String? = null,
    val chatRoom: DBChatRoom? = null,
    val messages: MutableList<DBChat> = mutableListOf(),
    val members: List<DBContact> = emptyList(),
    val connectionStatus: ConnectionStatus = ConnectionStatus.Disconnected
)

@HiltViewModel
class ChatViewModel @Inject constructor(
    private val chatRepository: ChatRepository,
    private val chatRoomDao: ChatRoomDao,
    private val contactDao: ContactDao
): ViewModel() {

    private val _state = MutableStateFlow(ChatState())
    val state = _state.asStateFlow()
    private val _messagesFlow = MutableSharedFlow<SocketMessage>()
    private val _connectionStatusFlow = MutableStateFlow<ConnectionStatus>(ConnectionStatus.Disconnected)
    val connectionStatus: StateFlow<ConnectionStatus> = _connectionStatusFlow.asStateFlow()

    private fun observeMessages(roomId: String){
        viewModelScope.launch {
            _messagesFlow.collectLatest { chatMessage ->
                when (chatMessage.type) {
                    MessageType.CHAT -> {
                        Log.d("ChatViewModel observeMessages", "Received chat message: $chatMessage")
                        val chatObj = chatMessage.obj as ChatObj
                        val dbChat = chatRoomDao.getMessageBySocketMessageId(chatMessage.id)
                        if (dbChat != null) {
                            chatRoomDao.updateMessage(dbChat.copy(chatId = chatObj.id))
                        } else {
                            chatRoomDao.insertMessage(chatMessage.toDBChat(roomId))
                        }
                        val currentMessages = chatRoomDao.getChatRoomMessages(roomId)
                        _state.update {
                            it.copy(messages = currentMessages)
                        }
                    }
                    MessageType.ONLINE -> {
                        val dbContact = contactDao.getByContactId(chatMessage.user?.id ?: "")
                        Log.d("ChatViewModel observeMessages", "User ${dbContact?.name} of id ${chatMessage.user?.id ?: ""} is Online")
                        if (dbContact != null) {
                            contactDao.update(dbContact.copy(isOnline = true, lastSeen = System.currentTimeMillis()))
                        }
                    }
                    MessageType.OFFLINE -> {
                        Log.d("ChatViewModel observeMessages", "User ${chatMessage.user?.id} is offline")
                    }
                    MessageType.READ -> {
                        Log.d("ChatViewModel observeMessages", "Message ${chatMessage.obj} is read by ${chatMessage.user?.id}")
                        val chatObj = chatMessage.obj as ChatObj
                        val dbChat = chatRoomDao.getMessageById(chatObj.id)
                        if (dbChat != null) {
                            chatRoomDao.updateMessage(dbChat.copy(isRead = true))
                        }
                    }
                    MessageType.READING -> {
                        Log.i("RaptSocket", "Message ${chatMessage.obj} is being read by ${chatMessage.user?.id}")
                    }
                    MessageType.AWAY -> {
                        Log.i("ChatViewModel observeMessages", "User ${chatMessage.user?.id} is away")
                    }
                    MessageType.TYPING -> {
                        Log.i("ChatViewModel observeMessages", "User ${chatMessage.user?.id} is typing")
                    }
                    MessageType.THINKING -> {
                        Log.i("ChatViewModel observeMessages", "User ${chatMessage.user?.id} is thinking")
                    }
                }
            }
        }
    }

    private fun observeConnectionStatus(){
        viewModelScope.launch {
            _connectionStatusFlow.collectLatest { connectionStatus ->
                _state.update {
                    it.copy(connectionStatus = connectionStatus)
                }
            }
        }
    }

    fun setupChat(contactId: String, roomId: String?){
        viewModelScope.launch {
            try {
                _state.update {
                    it.copy(isLoading = true)
                }
                val chatRoom = if (roomId == null) {
                    chatRepository.createChatRoom(listOf(contactId))
                } else {
                    chatRoomDao.getChatRoomById(roomId)
                }
                val members = chatRoom?.let { chatRoomDao.getChatRoomMembers(it.chatRoomId) }?.mapNotNull {contactDao.getByContactId(it) }
                val messages = chatRoom?.let { chatRoomDao.getChatRoomMessages(it.chatRoomId) }
                if (chatRoom != null) {
                    observeMessages(chatRoom.chatRoomId)
                    observeConnectionStatus()
                }
                _state.update {
                    it.copy(
                        isLoading = false,
                        messages = messages ?: mutableListOf(),
                        members = members ?: emptyList(),
                        chatRoom = chatRoom
                    )
                }
                chatRoom?.let { chatRepository.initializeChatSocket(it.chatRoomId, _messagesFlow, _connectionStatusFlow) }
            } catch (e: IOException) {
                Log.e("ChatViewModel setupChat","IOException: ${e.localizedMessage ?: "Could not reach server. Check your internet connection"}")
                _state.update {
                    it.copy(
                        isLoading = false,
                        error = "IOException: ${e.localizedMessage ?: "Could not reach server. Check your internet connection"}"
                    )
                }
            } catch (e: HttpException){
                Log.e("ChatViewModel setupChat","HttpException: ${e.response()} ${e.localizedMessage}")
                _state.update {
                    it.copy(
                        isLoading = false,
                        error = "Failed to create chat room: ${e.response()} ${e.localizedMessage}"
                    )
                }
            }

        }
    }

    fun sendChat(message: String) {
        viewModelScope.launch {
            try {
                _state.update {
                    it.copy(isLoading = true)
                }
                val dbChat = chatRepository.saveChat(message, state.value.chatRoom?.chatRoomId ?: "")
                chatRepository.sendMessage(dbChat.toSocketMessage())
                val currentMessages = chatRoomDao.getChatRoomMessages(state.value.chatRoom?.chatRoomId ?: "")
                _state.update {
                    it.copy(messages = currentMessages, isLoading = false)
                }
            } catch (e: Exception) {
                Log.e("ChatClient", "Error while sendingMessage", e)
            }

        }
    }
}