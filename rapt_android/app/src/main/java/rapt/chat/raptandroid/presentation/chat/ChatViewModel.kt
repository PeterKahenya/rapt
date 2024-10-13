package rapt.chat.raptandroid.presentation.chat

import android.util.Log
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import io.ktor.websocket.Frame
import io.ktor.websocket.WebSocketSession
import io.ktor.websocket.readText
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharedFlow
import kotlinx.coroutines.flow.asSharedFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import kotlinx.serialization.json.Json
import okio.IOException
import rapt.chat.raptandroid.data.model.Auth
import rapt.chat.raptandroid.data.repository.AuthRepository
import rapt.chat.raptandroid.data.repository.ChatObj
import rapt.chat.raptandroid.data.repository.ChatRepository
import rapt.chat.raptandroid.data.repository.MessageType
import rapt.chat.raptandroid.data.repository.SocketMessage
import rapt.chat.raptandroid.data.repository.User
import rapt.chat.raptandroid.data.source.ChatMessage
import rapt.chat.raptandroid.data.source.Contact
import retrofit2.HttpException
import javax.inject.Inject


data class ChatRoomState(
    val isLoading: Boolean = false,
    val isSending: Boolean = false,
    val error: String? = null,
    val messages: MutableList<ChatMessage> = mutableListOf(),
    val members: List<Contact> = emptyList(),
    val currentUser: Auth? = null
)

@HiltViewModel
class ChatViewModel @Inject constructor(
    private val chatRepository: ChatRepository,
    private val authRepository: AuthRepository
) : ViewModel() {

    private val _state = MutableStateFlow(ChatRoomState())
    val state = _state.asStateFlow()
    private var activeRoomId: String? = null

    fun initializeChatRoom(contactId: String, roomId: String?) {
           /*
            step 0. If roomId is not null, move to step 3 else move to step 1
            step 1. Check if chatroom exists for contactId by calling dbGetChatRoomByContactId if it exists return
            step 2. If not found, call createChatRoom to create via API and save to db by calling dbSaveChatRoom then repeating step 1
            step 3. Get chatroom members by calling dbGetChatRoomMembers
            step 4. Get chatroom messages by calling dbGetChatRoomMessages
            step 5. Connect to chat socket by calling connectToChatSocket
            step 6. Listen to messages by calling listenToMessages
            step 7. Send message by calling sendMessage
            step 8. Disconnect from chat socket by calling disconnectFromChatSocket
         */
            viewModelScope.launch {
                try {
                    _state.update {
                        it.copy(isLoading = true)
                    }

                    val auth = authRepository.auth()
                    _state.update {
                        it.copy(currentUser = auth)
                    }
                    activeRoomId = roomId ?: run {
                        chatRepository.dbGetChatRoomByContactId(contactId) ?: run {
                            val chatRoom = chatRepository.createChatRoom(contactId)
                            chatRepository.dbSaveChatRoom(chatRoom)
                            chatRoom.id
                        }
                    }
                    val chatRoomMembers = chatRepository.dbGetChatRoomMembers(activeRoomId!!)
                    _state.update {
                        it.copy(members = chatRoomMembers)
                    }
                    val chatRoomMessages = chatRepository.dbGetChatRoomMessages(activeRoomId!!)
                    _state.update {
                        it.copy(messages = chatRoomMessages)
                    }
                    _state.update {
                        it.copy(isLoading = false)
                    }
                    chatRepository.connectToChatSocket(roomId = activeRoomId!!).collect { it ->
                        println("ChatViewModel collect: $it")
                        val updatedChatRoomMessages = chatRepository.dbGetChatRoomMessages(
                            activeRoomId!!
                        )
                        _state.update {
                            it.copy(messages = updatedChatRoomMessages)
                        }
                    }

                } catch (e: IOException) {
                    val error = "initializeChatRoom IOException: ${e.localizedMessage ?: "Couldn't reach server. Check your internet connection"}"
                    println(error)
                    _state.update {
                        it.copy(
                            isLoading = false,
                            error = error
                        )
                    }
                } catch (e: HttpException){
                    println("initializeChatRoom HttpException: ${e.response()} ${e.localizedMessage}")
                    _state.update {
                        it.copy(
                            isLoading = false,
                            error = "Failed to create chat room: ${e.response()} ${e.localizedMessage}"
                        )
                    }
                }
            }
    }

    fun sendMessage(message: String) {
        viewModelScope.launch {
            try {
                _state.update {
                    it.copy(isSending = true)
                }
                val roomId = activeRoomId ?: throw Exception("Missing RoomID")
                val chatMessage = chatRepository.sendMessage(roomId, message, MessageType.CHAT)
                val updatedChatRoomMessages = chatRepository.dbGetChatRoomMessages(roomId)
                _state.update {
                    it.copy(messages = updatedChatRoomMessages, isSending = false)
                }
            } catch (e: Exception) {
                Log.e("ChatClient", "Error while sendingMessage", e)
            }
        }
    }

    fun isMyMessage(message: ChatMessage): Boolean {
        return if (_state.value.currentUser != null) {
            message.isFromMe(_state.value.currentUser!!)
        }else{
            false
        }
    }

    override fun onCleared() {
        super.onCleared()
        viewModelScope.launch {
            chatRepository.disconnectFromChatSocket()
        }
    }
}