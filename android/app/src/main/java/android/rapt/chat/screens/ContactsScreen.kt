package android.rapt.chat.screens

import android.content.Context
import android.content.Intent
import android.rapt.chat.ChatsListActivity
import android.rapt.chat.sources.DBContact
import android.rapt.chat.viewmodels.ContactsViewModel
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
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
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Search
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

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ContactsScreen(viewModel: ContactsViewModel) {
    val contactsState by viewModel.state.collectAsStateWithLifecycle()
    val context = LocalContext.current
    Scaffold (
        modifier = Modifier.padding(0.dp),
        topBar = {
            TopAppBar(
                colors = topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.primaryContainer,
                    titleContentColor = MaterialTheme.colorScheme.primary,
                ),
                navigationIcon = {
                    IconButton(
                        onClick = {
                            context.startActivity(Intent(context, ChatsListActivity::class.java))
                        }
                    ) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Go back")
                    }
                },
                title = {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Column {
                            Text(text = "Select Contact", style = MaterialTheme.typography.titleMedium)
                            Text(text = "${contactsState.contacts.size} contacts", style = MaterialTheme.typography.bodySmall)
                        }
                        if (contactsState.isLoading) {
                            Text(text = "Loading...")
                        }else{
                            IconButton(
                                onClick = {}
                            ) {
                                Icon(Icons.Default.Search, contentDescription = "Search Contact")
                            }
                        }
                    }
                }
            )

        }
    ) {
        if (contactsState.error != null) {
            Text(contactsState.error!!)
        }
        Column(modifier = Modifier
            .padding(it)
            .padding(16.dp)) {
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
                        }else {
                            ContactItem(contact, context)
                            HorizontalDivider(
                                modifier = Modifier.padding(horizontal = 8.dp),
                                thickness = 0.5.dp,
                                color = Color.Gray
                            )
                        }
                    }
                }
            }else{
                Text(text = "No contacts found")
            }
        }
    }
}

@Composable
fun ContactItem(contact: DBContact, context: Context) {

    Surface(
        modifier = Modifier
            .fillMaxWidth()
            .background(Color.LightGray),
        onClick = {

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