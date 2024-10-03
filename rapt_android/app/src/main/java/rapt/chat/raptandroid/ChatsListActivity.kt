package rapt.chat.raptandroid

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.hilt.navigation.compose.hiltViewModel
import dagger.hilt.android.AndroidEntryPoint
import rapt.chat.raptandroid.presentation.chats.ChatsScreen
import rapt.chat.raptandroid.presentation.chats.ChatsViewModel
import rapt.chat.raptandroid.presentation.ui.RaptTheme

@AndroidEntryPoint
class ChatsListActivity : ComponentActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // TODO ask for permission to receive notifications
        setContent {
            RaptTheme {
                val chatsViewModel = hiltViewModel<ChatsViewModel>()
                chatsViewModel.setUpChatRooms()
                ChatsScreen(chatsViewModel)
            }
        }
    }
}





