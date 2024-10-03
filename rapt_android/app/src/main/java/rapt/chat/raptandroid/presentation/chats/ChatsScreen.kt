package rapt.chat.raptandroid.presentation.chats

import android.content.Context
import android.content.Intent
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Edit
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FabPosition
import androidx.compose.material3.FloatingActionButton
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults.topAppBarColors
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import rapt.chat.raptandroid.ChatActivity
import rapt.chat.raptandroid.ContactsActivity
import rapt.chat.raptandroid.data.model.ChatRoom
import rapt.chat.raptandroid.data.model.Member
import rapt.chat.raptandroid.data.model.ProfileResponse
import rapt.chat.raptandroid.presentation.ErrorText
import rapt.chat.raptandroid.presentation.LoadingIndicator

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ChatsScreen(viewModel: ChatsViewModel) {
    val chatRoomsState by viewModel.state.collectAsStateWithLifecycle()
    val context = LocalContext.current
    Scaffold(floatingActionButton = {
        FloatingActionButton(onClick = {
            context.startActivity(Intent(context, ContactsActivity::class.java))
        }) {
            Row(
                modifier = Modifier.padding(horizontal = 16.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Icon(Icons.Default.Edit, contentDescription = "Add Chat")
                Text(text = "Add Chat")
            }
        }
    }, floatingActionButtonPosition = FabPosition.Center, topBar = {
        TopAppBar(colors = topAppBarColors(
            containerColor = MaterialTheme.colorScheme.primaryContainer,
            titleContentColor = MaterialTheme.colorScheme.primary,
        ), title = {
            Text(text = "Chats List")
        })
    }) {
        Column(modifier = Modifier.padding(it).padding(16.dp)) {
            if (chatRoomsState.isLoading) {
                LoadingIndicator()
            }
            if (chatRoomsState.error != null) {
                ErrorText(chatRoomsState.error!!)
            }
            if (chatRoomsState.chatRooms.isNotEmpty()) {
                LazyColumn {
                    items(chatRoomsState.chatRooms) { chatRoom ->
                        val otherUsers = chatRoom.members.filter { it.phone != chatRoomsState.currentUser?.phone }
                        ChatRoomItem(chatRoom, otherUsers, context)
                    }
                }
            }
        }
    }
}

@Composable
fun ChatRoomItem(chatRoom: ChatRoom, members: List<Member>, context: Context) {
    println("Chatroom Room Chats: ${chatRoom.room_chats}")
    Surface (
        modifier = Modifier.fillMaxWidth().background(Color.LightGray),
        onClick = {
            // Navigate to chat screen
            val intent = Intent(context, ChatActivity::class.java)
            intent.putExtra("contact", members[0].id)
            context.startActivity(intent)
        }
    ) {
        Column {
            Row(
                modifier = Modifier.padding(16.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                ChatsListAvatar(members[0].name)
                Spacer(modifier = Modifier.width(16.dp))
                Column {
                    Text(
                        text = members[0].name,
                        style = MaterialTheme.typography.titleMedium
                    )
                    Text(
                        text = chatRoom.room_chats.lastOrNull()?.message ?: "...",
                        style = MaterialTheme.typography.bodySmall
                    )
                }
                }
            }
            HorizontalDivider(modifier = Modifier.padding(horizontal = 8.dp), thickness = 0.5.dp, color = Color.Gray)
        }

    }



@Composable
fun ChatsListAvatar(name: String) {
    Surface(
        modifier = Modifier.size(50.dp),
        shape = CircleShape,
        color = MaterialTheme.colorScheme.secondary
    ) {
        Box(contentAlignment = Alignment.Center) {
            Text(
                text = name[0].toString(),
                color = Color.White,
                fontSize = 25.sp,
                fontWeight = FontWeight.Bold
            )
        }
    }
}