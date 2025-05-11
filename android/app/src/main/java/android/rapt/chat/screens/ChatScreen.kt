package android.rapt.chat.screens

import android.rapt.chat.sources.DBChat
import android.rapt.chat.viewmodels.ChatViewModel
import android.util.Log
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.wrapContentWidth
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.Send
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults.topAppBarColors
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.MutableState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ChatScreen(
    chatViewModel: ChatViewModel,
    contactId: String
){
    val chatState by chatViewModel.state.collectAsStateWithLifecycle()
    val connectionStatus by chatViewModel.connectionStatus.collectAsStateWithLifecycle()
    val contact = chatState.members.find { it.contactId == contactId }
    Log.i("ChatScreen", "Contact: $contact")
    if (chatState.isLoading) {
        Text("Loading...")
    }
    if (chatState.error != null) {
        Text(text = "Error: ${chatState.error}")
    }
    Scaffold(
        topBar = {
            TopAppBar(
                colors = topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.primaryContainer,
                    titleContentColor = MaterialTheme.colorScheme.primary,
                ),
                title = {
                    Column {
                        contact?.name?.let { Text(text = it, style = MaterialTheme.typography.titleLarge) }
                        Text(text = "Last Seen ${contact?.lastSeen?: "Never"}",style = MaterialTheme.typography.bodySmall)
                        Text(text = "Connection Status: $connectionStatus", style = MaterialTheme.typography.bodySmall)
                    }
                }
            )

        },
        bottomBar = {
            MessageBox(sendMessage = { msg: String -> chatViewModel.sendChat( msg ) })
        }
    ){
        MessagesList(modifier = Modifier.padding(it), ml = chatState.messages, chatState.isLoading, chatState.error)
    }
}

@Composable
fun MessageBox(sendMessage: (message: String) -> Unit) {
    val message: MutableState<String> = remember { mutableStateOf("") }
    Row(
        modifier = Modifier.fillMaxWidth(),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.Center
    ) {
        OutlinedTextField(value = message.value,
            onValueChange = {
                message.value = it
            },
            modifier = Modifier
                .weight(1f)
                .padding(10.dp)
                .clip(RoundedCornerShape(30.dp))
                .background(MaterialTheme.colorScheme.surfaceVariant),
            colors = OutlinedTextFieldDefaults.colors(
                unfocusedBorderColor = Color.Transparent,
                focusedBorderColor = Color.Transparent,
                errorBorderColor = Color.Transparent,
            ),
            placeholder = { Text("Enter your message...", style = MaterialTheme.typography.bodyLarge)},
            textStyle = MaterialTheme.typography.bodyLarge,
            trailingIcon = {
                IconButton(
                    enabled = message.value.isNotEmpty(),
                    onClick = {
                        sendMessage(message.value)
                        message.value = ""
                    }
                ) {
                    if (message.value.isNotEmpty()){
                        Icon(Icons.AutoMirrored.Filled.Send, contentDescription = "Send", tint = MaterialTheme.colorScheme.primary)
                    }
                }
            })
    }
}

@Composable
fun MessagesList(modifier: Modifier, ml: List<DBChat>, isLoading: Boolean, error: String?) {
    val listState = rememberLazyListState()
    Column(modifier = modifier.fillMaxSize()) {
        if (ml.isEmpty()) {
            Text(
                text = "No chats yet!",
                color = Color.Gray,
                textAlign = TextAlign.Center,
                modifier = Modifier.fillMaxSize().padding(vertical = 300.dp)
            )
        }
        LazyColumn(
            state = listState,
            verticalArrangement = Arrangement.spacedBy(4.dp), // Add spacing between messages
            contentPadding = PaddingValues(horizontal = 8.dp, vertical = 8.dp) // Add padding to the list
        ) {
            items(ml) {
                val isUser = it.senderId == "user"
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .wrapContentWidth(if (isUser) Alignment.End else Alignment.Start)
                        .padding(horizontal = 1.dp, vertical = 2.dp)
                ) {
                    Box(
                        modifier = Modifier
                            .clip(RoundedCornerShape(10.dp)) // Rounded corners for the bubble
                            .background(if (isUser) MaterialTheme.colorScheme.surfaceVariant else MaterialTheme.colorScheme.surface)
                            .padding(5.dp)
                    ) {
                        Text(text = it.message, style = MaterialTheme.typography.bodyMedium)
                    }
                }
            }
        }
        LaunchedEffect(ml.size) {
            if (ml.isNotEmpty()) {
                listState.animateScrollToItem(ml.size - 1)
            }
        }
        if (isLoading) {
            LinearProgressIndicator(
                modifier = Modifier.width(50.dp).height(2.dp).padding(horizontal = 5.dp),
                color = MaterialTheme.colorScheme.primary,
                trackColor = MaterialTheme.colorScheme.tertiary
            )
        }
        if (error !== null){
            Box(
                modifier = Modifier
                    .padding(10.dp)
                    .clip(RoundedCornerShape(10.dp)) // Rounded corners for the bubble
                    .background(MaterialTheme.colorScheme.errorContainer)
                    .padding(8.dp)
            ){
                Text(text = error, style = MaterialTheme.typography.labelSmall)
            }
        }
    }
}