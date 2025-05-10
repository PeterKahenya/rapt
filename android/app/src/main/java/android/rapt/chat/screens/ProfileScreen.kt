package android.rapt.chat.screens

import android.content.Intent
import android.rapt.chat.ChatsListActivity
import android.rapt.chat.models.User
import android.rapt.chat.viewmodels.ProfileViewModel
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
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
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.compose.collectAsStateWithLifecycle

@Composable
fun ProfileScreen(
    profileViewModel: ProfileViewModel
) {
    val profileState by profileViewModel.profileState.collectAsStateWithLifecycle()
    Column(
        modifier = Modifier
            .padding(16.dp)
            .fillMaxSize(),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        if (profileState.user != null) {
            ProfileContent(profileState.user!!, profileViewModel)
        }
        if (profileState.isLoading) {
            Text("Loading...")
        }
        if (profileState.error != null) {
            Text(profileState.error!!)
        }
    }
}

@Composable
fun ProfileContent(profile: User, profileViewModel: ProfileViewModel) {
    val name = remember { mutableStateOf(profile.name) }
    val context = LocalContext.current
    Avatar(profile)
    Spacer(modifier = Modifier.height(16.dp))
    TextField(value = name.value, onValueChange = { name.value = it }, label = { Text("Name") })
    Spacer(modifier = Modifier.height(8.dp))
    TextField(value = profile.phone,
        onValueChange = { },
        label = { Text("Name") },
        enabled = false
    )
    Spacer(modifier = Modifier.height(8.dp))
    Button(onClick = {
        profileViewModel.updateProfile(profile.id, name.value, null)
        profileViewModel.getProfile()
    }) {
        Text("Update Profile")
    }
    Spacer(modifier = Modifier.height(8.dp))
    Button(onClick = {
        context.startActivity(Intent(context, ChatsListActivity::class.java))
    }) {
        Text("Chats")
    }
}

@Composable
fun Avatar(profile: User) {
    Surface(
        modifier = Modifier.size(100.dp),
        shape = CircleShape,
        color = MaterialTheme.colorScheme.secondary
    ) {
        Box(contentAlignment = Alignment.Center) {
            Text(
                text = profile.name[0].toString(),
                color = Color.White,
                fontSize = 50.sp,
                fontWeight = FontWeight.Bold
            )
        }
    }
}