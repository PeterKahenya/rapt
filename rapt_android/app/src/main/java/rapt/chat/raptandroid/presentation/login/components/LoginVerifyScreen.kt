package rapt.chat.raptandroid.presentation.login.components

import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.material3.Button
import androidx.compose.material3.Text
import androidx.compose.material3.TextField
import androidx.compose.runtime.Composable
import androidx.compose.runtime.MutableState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import rapt.chat.raptandroid.R
import rapt.chat.raptandroid.presentation.login.LoginViewModel

@Composable
fun LoginScreen(
    loginViewModel: LoginViewModel
) {
    val loginState by loginViewModel.state.collectAsStateWithLifecycle()
    val phone: MutableState<String> = remember { mutableStateOf("") }
    Column(
        horizontalAlignment = Alignment.Start,
        modifier = Modifier
            .fillMaxSize()
            .background(Color.White)
            .padding(30.dp)
            .padding(top = 50.dp)
    ) {
        Image(
            painter = painterResource(id = R.drawable.logo),
            contentDescription = "Rapt Logo",
            modifier = Modifier.testTag("loginLogo")
                .size(130.dp)
        )
        Text(
            text = "Confirm Your Number",
            color = Color(0xFF008080),
            fontSize = 14.sp,
            fontWeight = FontWeight.Bold,
            modifier = Modifier.testTag("loginTitle")
                .padding(top = 40.dp)
                .padding(bottom = 40.dp)
        )
        TextField(
            value = phone.value,
            onValueChange = {
                phone.value = it
            },
            label = { Text(text = "254 712 345 678") },
            modifier = Modifier.testTag("loginPhoneField")
                .fillMaxWidth()
        )
        Button(
            onClick = { loginViewModel.login(phone.value) },
            modifier = Modifier.testTag("loginNextButton")
                .padding(top = 100.dp)
                .align(Alignment.End)
                .width(150.dp)
        ) {
            Text(text = "Next")
        }
        if (!loginState.error.isNullOrEmpty()) {
            Text(text = loginState.error?: "An unexpected error occurred")
        }
        if (loginState.isLoading) {
            Text(text = "Loading...")
        }
        if (loginState.loginResponse != null) {
            Text(text = "SMS sent")
        }
    }
}


