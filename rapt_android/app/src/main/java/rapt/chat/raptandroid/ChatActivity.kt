package rapt.chat.raptandroid

import android.os.Bundle
import android.util.Log
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.material3.Button
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TextField
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults.topAppBarColors
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.MutableState
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import androidx.lifecycle.viewmodel.compose.viewModel
import dagger.hilt.android.AndroidEntryPoint
import dagger.hilt.android.lifecycle.HiltViewModel
import io.ktor.websocket.Frame
import io.ktor.websocket.WebSocketSession
import io.ktor.websocket.readText
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharedFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asSharedFlow
import kotlinx.coroutines.launch
import kotlinx.serialization.json.Json
import rapt.chat.raptandroid.data.model.ChatRoom
import rapt.chat.raptandroid.data.model.Room
import rapt.chat.raptandroid.data.model.RoomChat
import rapt.chat.raptandroid.data.repository.ChatRepository
import rapt.chat.raptandroid.data.repository.Message
import rapt.chat.raptandroid.data.repository.MessageType
import rapt.chat.raptandroid.presentation.ui.RaptTheme
import javax.inject.Inject


@HiltViewModel
class ChatViewModel @Inject constructor(
    private val chatRepository: ChatRepository,
) : ViewModel() {
    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading
    private val _error = MutableStateFlow<String?>(null)
    val error: StateFlow<String?> = _error
    private val _chatRoom = MutableStateFlow<ChatRoom?>(null)
    val chatRoom: StateFlow<ChatRoom?> = _chatRoom
    private val _messages = MutableStateFlow<List<String>>(emptyList())
    private val _messagesFlow = MutableSharedFlow<Message>()
    val messages: SharedFlow<Message> = _messagesFlow.asSharedFlow()


    fun localStartListening(socket: WebSocketSession?) = CoroutineScope(Dispatchers.IO).launch {
        try {
            socket?.let { socket ->
                for (frame in socket.incoming) {
                    frame as? Frame.Text ?: continue
                    val receivedText = frame.readText()
                    println("ChatClient Received message: $receivedText")
                    Log.i("ChatClient", "Message: $receivedText")
                    val json = Json { ignoreUnknownKeys = true }
                    val chatMessage = json.decodeFromString<Message>(receivedText)
                    println("ChatClient Message: $chatMessage")
                    _messagesFlow.emit(chatMessage)
                }
            }
        } catch (e: Exception) {
            Log.e("ChatClient", "Error while listening", e)
        }
    }


    fun initializeChatRoom(contactIds: List<String>) {
        /*
            Create or Get Chatroom
            Connect to Chatroom socket
         */
        println("initializeChatRoom: $contactIds")
        viewModelScope.launch {
            try {
                _isLoading.value = true
                _error.value = null
                val chatRoom = chatRepository.createChatRoom(contactIds)
                println("initializeChatRoom: $chatRoom")
                val chatSocket = chatRepository.connectToChatSocket(chatRoom.id)
                localStartListening(chatSocket)
                chatRepository.listenToMessages(_messagesFlow)
                _chatRoom.value = chatRoom
                _isLoading.value = false
            } catch (e: Exception) {
                println("Failed to create chat room: ${e.localizedMessage}")
                _error.value = "Failed to create chat room: ${e.localizedMessage}"
                _isLoading.value = false
            }
        }
    }

    fun sendMessage(message: String) {
        viewModelScope.launch {
            chatRepository.sendMessage(message)
        }
    }

    override fun onCleared() {
        super.onCleared()
        viewModelScope.launch {
            chatRepository.disconnectFromChatSocket()
        }
    }


}

@AndroidEntryPoint
class ChatActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val contactId = intent.getStringExtra("contact")
        println("ChatActivity contactId: $contactId")

        setContent {
            RaptTheme {
                val newChatsList = mutableListOf<Message>()
                val chatViewModel: ChatViewModel = hiltViewModel<ChatViewModel>()
                if (contactId != null) {
                    chatViewModel.initializeChatRoom(listOf(contactId))
                    ChatScreen(contactId, chatViewModel, newChatsList)
                } else {
                    Text(text = "Invalid Contact ID")
                }
            }
        }
    }
}

@Composable
fun ChatScreen(
    contactId: String,
    chatViewModel: ChatViewModel,
    newChatsList: MutableList<Message>
) {
    val chatRoom by chatViewModel.chatRoom.collectAsState(null)
    val isLoading by chatViewModel.isLoading.collectAsState(false)
    val error by chatViewModel.error.collectAsState(null)
    val messages by chatViewModel.messages.collectAsState(null)

//    chatViewModel.createChatRoom(contactId)

    println("ChatScreen: $messages")
    if (messages != null) {
        newChatsList.add(messages!!)
        println("NewChatsList Updated Count: ${newChatsList.size}")
    }

    if (isLoading) {
        Text(text = "Loading...")
    }
    if (error != null) {
        Text(text = "Error: $error")
    }
    if (chatRoom != null) {
        println("Chat Room ID: ${chatRoom!!.id}")
        println("Chat Screen for Contact: $contactId")
        ChatScreenContent(
            chatRoom!!,
            sendMessage = { msg: String -> chatViewModel.sendMessage(msg) },
            newChatsList
        )
    }
//    Text(text = messages?.obj?.get("message")!!)
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ChatScreenContent(
    chatRoom: ChatRoom,
    sendMessage: (message: String) -> Unit,
    ml: MutableList<Message>
) {
    val message: MutableState<String> = remember { mutableStateOf("") }
    val listState = rememberLazyListState()
    Scaffold(
        topBar = {
            TopAppBar(
                colors = topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.primaryContainer,
                    titleContentColor = MaterialTheme.colorScheme.primary,
                ),
                title = {
                    Text("Chatting with ${chatRoom.members[0].name} and ${chatRoom.members[1].name}")
                }
            )
        },
        bottomBar = {
            Row(
                modifier = Modifier.padding(5.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                TextField(
                    value = message.value,
                    onValueChange = {
                        message.value = it
                    },
                    label = { Text("Type a message...") },
                )
                Button(
                    onClick = {
                        sendMessage(message.value)
                        message.value = ""
                    }
                ) {
                    Text(text = "Send")
                }
            }

        }
    ) {
        Column(modifier = Modifier.fillMaxSize()) {
            LazyColumn(
                modifier = Modifier.padding(it).weight(1f),
                state = listState
            ) {
                items(chatRoom.room_chats.size) { index ->
                    Text(
                        text = chatRoom.room_chats[index].message,
                        modifier = Modifier
                            .padding(10.dp)
                            .background(MaterialTheme.colorScheme.background)
                    )
                }
                items(ml.size) { index ->
                    if (ml[index].obj != null) {
                        Text(
                            text = ml[index].obj?.message!!,
                            modifier = Modifier
                                .padding(10.dp)
                                .background(MaterialTheme.colorScheme.background)
                        )
                    }
                }
            }
            LaunchedEffect(ml.size+chatRoom.room_chats.size) {
                if (ml.size+chatRoom.room_chats.size > 0 && ml.isNotEmpty() && chatRoom.room_chats.isNotEmpty()) {
                    listState.animateScrollToItem(ml.size+chatRoom.room_chats.size - 1)
                }
            }
        }
    }
}