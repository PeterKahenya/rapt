package rapt.chat.raptandroid.presentation.welcome

import android.content.Intent
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import rapt.chat.raptandroid.ChatsListActivity
import rapt.chat.raptandroid.LoginActivity
import rapt.chat.raptandroid.R
import rapt.chat.raptandroid.presentation.ErrorText
import rapt.chat.raptandroid.presentation.LoadingIndicator

@Composable
fun WelcomeScreen(viewModel: WelcomeViewModel){
    val authStatus by viewModel.isAuthenticated.collectAsStateWithLifecycle()

    if (authStatus.isLoading){
        LoadingIndicator()
    }
    if (authStatus.error != null){
        ErrorText(authStatus.error!!)
    }
    if (authStatus.isAuthenticated){
        println("Authenticated")
        LocalContext.current.startActivity(Intent(LocalContext.current, ChatsListActivity::class.java))
    } else {
        println("Not Authenticated")
        WelcomeContent()
    }
}

@Composable
fun WelcomeContent() {
    val context = LocalContext.current
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xFFDFDFDF)),
        contentAlignment = Alignment.Center,
    ) {
        Image(
            painter = painterResource(id = R.drawable.main_bg),
            contentDescription = "Rapt Background Image",
            modifier = Modifier
                .height(1000.dp)
                .width(1000.dp)
        )
        Column(
            horizontalAlignment = Alignment.End,
            modifier = Modifier
                .fillMaxSize()
                .padding(horizontal = 50.dp),
            verticalArrangement = Arrangement.Center
        ) {
            Image(
                painter = painterResource(id = R.drawable.logo),
                contentDescription = "Rapt Logo",
                modifier = Modifier.size(120.dp)
            )
            Spacer(Modifier.height(120.dp))
            Button(
                onClick = {
                    context.startActivity(Intent(context, LoginActivity::class.java))
                },
                modifier = Modifier
                    .height(40.dp)
                    .width(100.dp),
                colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF008080))
            ) {
                Text(text = "Login", color = Color.White)
            }
        }
    }
}