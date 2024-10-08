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
    val error: String? = null,
    val messages: MutableList<ChatMessage> = mutableListOf(),
    val members: List<Contact> = emptyList()
)

@HiltViewModel
class ChatViewModel @Inject constructor(
    private val chatRepository: ChatRepository,
) : ViewModel() {
    private val _state = MutableStateFlow(ChatRoomState())
    val state = _state.asStateFlow()
    private val _messages = MutableStateFlow<List<String>>(emptyList())
    private val _messagesFlow = MutableSharedFlow<SocketMessage>()
    val messages: SharedFlow<SocketMessage> = _messagesFlow.asSharedFlow()

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
                    var activeRoomId: String?
                    if (roomId == null) {
//                        println("roomId is null")
                        activeRoomId = chatRepository.dbGetChatRoomByContactId(contactId)
//                        println("activeRoomId: $activeRoomId")
                        if (activeRoomId == null) {
                            val chatRoom = chatRepository.createChatRoom(contactId)
                            chatRepository.dbSaveChatRoom(chatRoom)
                            activeRoomId = chatRoom.id
                        }
                    }else {
                        activeRoomId = roomId
                    }
                    println("activeRoomId: $activeRoomId")
                    val chatRoomMembers = chatRepository.dbGetChatRoomMembers(activeRoomId)
                    println("chatRoomMembers: $chatRoomMembers")
                    _state.update {
                        it.copy(members = chatRoomMembers)
                    }
                    val chatRoomMessages = chatRepository.dbGetChatRoomMessages(activeRoomId)
                    println("chatRoomMessages: $chatRoomMessages")
                    _state.update {
                        it.copy(messages = chatRoomMessages)
                    }
                    val chatSocket = chatRepository.connectToChatSocket(activeRoomId)
                    localStartListening(chatSocket)
                    chatRepository.listenToMessages(_messagesFlow)
                    _state.update {
                        it.copy(isLoading = false)
                    }
                } catch (e: IOException) {
                    val error = "initializeChatRoom IOException: ${e.localizedMessage ?: "Couldn't reach server. Check your internet connection"}"
                    println(error)
                    _state.value = ChatRoomState(
                                    isLoading = false,
                                    error = error
                    )
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





    private fun localStartListening(socket: WebSocketSession?) = CoroutineScope(Dispatchers.IO).launch {
        try {
            socket?.let { socket ->
                for (frame in socket.incoming) {
                    frame as? Frame.Text ?: continue
                    val receivedText = frame.readText()
                    Log.i("ChatClient", "Message: $receivedText")
                    val json = Json { ignoreUnknownKeys = true }
                    val socketMessage = json.decodeFromString<SocketMessage>(receivedText)
                    Log.i("ChatClient", "Socket Message: $socketMessage")
                    // save message to db
                    val dbMessage = chatRepository.dbSaveChatMessage(socketMessage)
                    // update state
                    val currentMessages = state.value.messages
                    currentMessages.add(dbMessage)
                    _state.value = state.value.copy(messages = currentMessages)
                }
            }
        } catch (e: Exception) {
            Log.e("ChatClient", "Error while listening", e)
        }
    }




    fun sendMessage(message: String) {
        viewModelScope.launch {
            try {
                _state.value = ChatRoomState(isLoading = true)
                val socketMessage = chatRepository.sendMessage(message)
                val dbMessage = chatRepository.dbSaveChatMessage(socketMessage)
                // update state
                val currentMessages = state.value.messages
                currentMessages.add(dbMessage)
                _state.value = state.value.copy(messages = currentMessages, isLoading = false)
            } catch (e: Exception) {
                Log.e("ChatClient", "Error while sendingMessage", e)
            }

        }
    }

    override fun onCleared() {
        super.onCleared()
        viewModelScope.launch {
            chatRepository.disconnectFromChatSocket()
        }
    }
}