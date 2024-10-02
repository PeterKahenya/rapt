package rapt.chat.raptandroid.presentation.profile

import android.content.Intent
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextField
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.core.content.ContextCompat.startActivity
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import rapt.chat.raptandroid.ChatsListActivity
import rapt.chat.raptandroid.data.model.ProfileResponse
import rapt.chat.raptandroid.presentation.ErrorText
import rapt.chat.raptandroid.presentation.LoadingIndicator

@Composable
fun ProfileScreen(
    profileViewModel: ProfileViewModel
){
    val profileState by profileViewModel.profileState.collectAsStateWithLifecycle()

    if(profileState.isLoading){
        LoadingIndicator()
    }
    if (profileState.error != null) {
        ErrorText(profileState.error!!)
    }
    if(profileState.profileResponse != null){
        ProfileContent(profileState.profileResponse!!, profileViewModel)

    }

}

@Composable
fun ProfileContent(profile: ProfileResponse, profileViewModel: ProfileViewModel){
    val name = remember { mutableStateOf(profile.name) }
    val context = LocalContext.current
    Column (
        modifier = Modifier.padding(16.dp).fillMaxSize(),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Avatar(profile)
        Spacer(modifier = Modifier.height(16.dp))
        TextField(
            value = name.value,
            onValueChange = { name.value = it },
            label = { Text("Name") }
        )
        Spacer(modifier = Modifier.height(8.dp))
        TextField(
            value = profile.phone ?: "",
            onValueChange = { },
            label = { Text("Name") },
            enabled = false
        )
        Spacer(modifier = Modifier.height(8.dp))
        Button(
            onClick = {
                profileViewModel.updateProfile(profile.id,name.value, null)
                profileViewModel.getProfile()
            }
        ) {
            Text("Update Profile")
        }
        Spacer(modifier = Modifier.height(8.dp))
        Button(
            onClick = {
                val intent = Intent(context, ChatsListActivity::class.java)
                startActivity(context,intent, null)
            }
        ) {
            Text("Chats")
        }
    }

}

@Composable
fun Avatar(profile: ProfileResponse){
    Text(
        text = profile.name[0].toString(),
        style = MaterialTheme.typography.headlineLarge,
        color = Color.White,
        modifier = Modifier.padding(8.dp).width(100.dp).height(100.dp).background(Color(0xFF008080))
    )
}