package rapt.chat.raptandroid

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.material3.Text
import androidx.hilt.navigation.compose.hiltViewModel
import dagger.hilt.android.AndroidEntryPoint
import rapt.chat.raptandroid.presentation.chat.ChatScreen
import rapt.chat.raptandroid.presentation.chat.ChatViewModel
import rapt.chat.raptandroid.presentation.ui.RaptTheme

@AndroidEntryPoint
class ChatActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val contactId = intent.getStringExtra("contactId")
        val roomId = intent.getStringExtra("roomId")
        println("ChatActivity contactId: $contactId roomId: ${roomId?: "null"}")
        setContent {
            RaptTheme {
                val chatViewModel: ChatViewModel = hiltViewModel<ChatViewModel>()
                if (contactId != null) {
                    chatViewModel.initializeChatRoom(contactId, roomId)
                    ChatScreen(contactId, chatViewModel)
                } else {
                    Text(text = "Invalid Contact ID")
                }
            }
        }
    }
}

