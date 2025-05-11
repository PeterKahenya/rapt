package android.rapt.chat

import android.os.Bundle
import android.rapt.chat.screens.ChatScreen
import android.rapt.chat.theme.RaptTheme
import android.rapt.chat.viewmodels.ChatViewModel
import android.util.Log
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.material3.Text
import androidx.hilt.navigation.compose.hiltViewModel
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class ChatActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val contactId = intent.getStringExtra("contactId")
        val roomId = intent.getStringExtra("roomId")
        Log.i("ChatActivity onCreate","contactId: $contactId roomId: ${roomId?: "null"}")
        setContent {
            RaptTheme {
                val viewModel = hiltViewModel<ChatViewModel>()
                if (contactId != null) {
                    viewModel.setupChat(contactId, roomId)
                    ChatScreen(viewModel, contactId)
                }else if (roomId != null){
                    viewModel.setupChat("", roomId)
                    ChatScreen(viewModel, "")
                } else {
                    Text("No contactId or roomId provided")
                }
            }
        }
    }
}