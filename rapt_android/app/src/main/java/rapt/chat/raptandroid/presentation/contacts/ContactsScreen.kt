package rapt.chat.raptandroid.presentation.contacts

import android.content.Context
import android.content.Intent
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Search
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
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
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import rapt.chat.raptandroid.ChatActivity
import rapt.chat.raptandroid.data.source.Contact
import rapt.chat.raptandroid.presentation.ErrorText
import rapt.chat.raptandroid.presentation.LoadingIndicator
import rapt.chat.raptandroid.presentation.chats.ChatRoomItem
import rapt.chat.raptandroid.presentation.profile.Avatar

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ContactsScreen(viewModel: ContactsViewModel) {
    val contactsState by viewModel.state.collectAsStateWithLifecycle()
    val context = LocalContext.current
    println("ContactsState: ${contactsState.contacts.size}")
    Scaffold (
        topBar = {
            TopAppBar(colors = topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.primaryContainer,
                    titleContentColor = MaterialTheme.colorScheme.primary,
                ),
                title = {
                    Row(
                        modifier = Modifier.padding(horizontal = 16.dp).fillMaxWidth(),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Text(text = "Contacts")
                        if (contactsState.isLoading) {
                            LoadingIndicator()
                        }else{
                            IconButton(
                                onClick = {}
                            ) {
                                Icon(Icons.Default.Search, contentDescription = "Search Contact")
                            }
                        }
                    }
                })
        }
    ) {
        if (contactsState.error != null) {
            ErrorText(contactsState.error!!)
        }
        Column(modifier = Modifier.padding(it).padding(16.dp)) {
            if (contactsState.contacts.isNotEmpty()) {
                LazyColumn {
                    items(contactsState.contacts) { contact ->
                        if (contact.isActive) {
                            ContactItem(contact, context)
                            HorizontalDivider(
                                modifier = Modifier.padding(horizontal = 8.dp),
                                thickness = 0.5.dp,
                                color = Color.Gray
                            )
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun ContactItem(contact: Contact, context: Context) {

    Surface(
        modifier = Modifier.fillMaxWidth().background(Color.LightGray),
        onClick = {
            println("Selected Contact: $contact")
            val intent = Intent(context, ChatActivity::class.java)
            intent.putExtra("contactId", contact.contactId)
            context.startActivity(intent)
        }
    ) {
            Row (
                modifier = Modifier.padding(16.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                ContactAvatar(name = contact.name)
                Spacer(modifier = Modifier.width(16.dp))
                Column {
                    Text(
                        text = contact.name,
                        style = MaterialTheme.typography.titleMedium
                    )
                    Text(
                        text = contact.phone,
                        style = MaterialTheme.typography.bodySmall
                    )
                }
            }
    }
}


@Composable
fun ContactAvatar(name: String) {
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