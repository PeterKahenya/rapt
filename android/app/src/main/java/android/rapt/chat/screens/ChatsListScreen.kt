package android.rapt.chat.screens

import android.content.Context
import android.content.Intent
import android.rapt.chat.ChatActivity
import android.rapt.chat.ContactsActivity
import android.rapt.chat.sources.DBChatRoomWithMembersAndMessages
import android.rapt.chat.viewmodels.ChatsListViewModel
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Edit
import androidx.compose.material.icons.filled.Search
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FabPosition
import androidx.compose.material3.FloatingActionButton
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
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
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ChatsListScreen(
    viewModel: ChatsListViewModel
) {
    val chatRoomsState by viewModel.state.collectAsStateWithLifecycle()
    val context = LocalContext.current
    Scaffold(
        floatingActionButton = {
            FloatingActionButton(onClick = {
                context.startActivity(Intent(context, ContactsActivity::class.java))
            }) {
                Row(
                    modifier = Modifier.padding(horizontal = 16.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(Icons.Default.Edit, contentDescription = "Add Chat")
                    Text(text = "Chat")
                }
            }
        },
        floatingActionButtonPosition = FabPosition.End,
        topBar = {
            TopAppBar(colors = topAppBarColors(
                containerColor = MaterialTheme.colorScheme.primaryContainer,
                titleContentColor = MaterialTheme.colorScheme.primary,
            ), title = {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text(text = "Rapt Chat")
                    IconButton(
                        onClick = {}
                    ) {
                        Icon(Icons.Default.Search, contentDescription = "Add Chat")
                    }
                }
            })
        }
    ) {
        Column(modifier = Modifier.padding(it).padding(16.dp)) {
            if (chatRoomsState.rooms.isNotEmpty()) {
                LazyColumn {
                    items(chatRoomsState.rooms) { room ->
                        ChatRoomItem(room, context)
                        HorizontalDivider(
                            modifier = Modifier.padding(horizontal = 8.dp),
                            thickness = 0.5.dp,
                            color = Color.Gray
                        )
                    }
                }
            }else{
                Text(text = "No chats yet")
            }
        }
    }
}

@Composable
fun ChatRoomItem(room: DBChatRoomWithMembersAndMessages, context: Context) {
    val contact = room.members.firstOrNull()
    val latestMessage = room.chats.firstOrNull()
    Surface(
        modifier = Modifier
            .fillMaxWidth()
            .background(Color.LightGray),
        onClick = {
            val intent = Intent(context, ChatActivity::class.java)
            intent.putExtra("roomId", room.room.chatRoomId)
            context.startActivity(intent)
        }
    ) {
        Row (
            modifier = Modifier.padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            if (contact != null) {
                ContactAvatar(name = contact.name)
            }
            Spacer(modifier = Modifier.width(16.dp))
            Column {
                if (contact != null) {
                    Text(
                        text = contact.name,
                        style = MaterialTheme.typography.titleMedium
                    )
                }
                if (latestMessage != null) {
                    Text(
                        text = latestMessage.message,
                        style = MaterialTheme.typography.bodySmall
                    )
                }
            }
        }
    }
}

