package rapt.chat.raptandroid.presentation.chat

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
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
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import rapt.chat.raptandroid.data.source.ChatMessage
import rapt.chat.raptandroid.presentation.ErrorText
import rapt.chat.raptandroid.presentation.LoadingIndicator

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ChatScreen(
    contactId: String,
    chatViewModel: ChatViewModel
) {
    val state by chatViewModel.state.collectAsStateWithLifecycle()
    if (state.isLoading) {
        LoadingIndicator()
    }
    if (state.error != null) {
       ErrorText(text = "Error: ${state.error}")
    }
    if (!state.isLoading && state.error == null) {
        Scaffold(
            topBar = {
                TopAppBar(
                    colors = topAppBarColors(
                        containerColor = MaterialTheme.colorScheme.primaryContainer,
                        titleContentColor = MaterialTheme.colorScheme.primary,
                    ),
                    title = {
                        Text("Chatting with ${state.members[0].name} and ${state.members[1].name}")
                    }
                )
            },
            bottomBar = { MessageBox(sendMessage = { msg: String -> chatViewModel.sendMessage(msg)} ) }
        ){
            MessagesList(modifier = Modifier.padding(it), ml = state.messages)
        }
    }
}

@Composable
fun MessageBox(sendMessage: (message: String) -> Unit){
    val message: MutableState<String> = remember { mutableStateOf("") }
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

@Composable
fun MessagesList(modifier: Modifier, ml: MutableList<ChatMessage>){
    val listState = rememberLazyListState()
    Column(modifier = modifier.fillMaxSize()) {
        LazyColumn(
            modifier = modifier
                .weight(1f),
            state = listState
        ) {
            items(ml) {
                Text(
                    text = it.message,
                    modifier = Modifier
                        .padding(10.dp)
                        .background(MaterialTheme.colorScheme.background)
                )
            }
        }
        LaunchedEffect(ml.size) {
            if (ml.size > 0) {
                listState.animateScrollToItem(ml.size - 1)
            }
        }
    }
}