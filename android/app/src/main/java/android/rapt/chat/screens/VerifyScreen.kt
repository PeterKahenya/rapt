package android.rapt.chat.screens

import android.content.Intent
import android.rapt.chat.LoginActivity
import android.rapt.chat.R
import android.rapt.chat.viewmodels.VerifyViewModel
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
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
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.compose.collectAsStateWithLifecycle

@Composable
fun VerifyScreen(
    verifyViewModel: VerifyViewModel,
    phone: String
) {

    val verifyState by verifyViewModel.state.collectAsStateWithLifecycle()
    val code: MutableState<String> = remember { mutableStateOf("") }
    val context = LocalContext.current

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
            modifier = Modifier
                .testTag("loginLogo")
        )
        Text(
            text = "Enter SMS Code",
            color = Color(0xFF008080),
            fontSize = 14.sp,
            fontWeight = FontWeight.Bold,
            modifier = Modifier
                .testTag("smsTitle")
                .padding(top = 40.dp)
                .padding(bottom = 40.dp)
        )
        TextField(
            value = code.value,
            onValueChange = {
                code.value = it
            },
            label = { Text(text = "e.g. T9GTA8") },
            modifier = Modifier
                .testTag("loginOTPField")
                .fillMaxWidth()
                .padding(top = 20.dp)
        )
        if (verifyState.isLoading) {
            Text(text = "Loading...")
        }
        if (verifyState.error != null) {
            Text(text = verifyState.error!!)
        }
        Row {
            Button(
                onClick = {
                    val intent = Intent(context, LoginActivity::class.java)
                    context.startActivity(intent)
                },
                modifier = Modifier
                    .testTag("loginVerifyBackButton")
                    .padding(top = 100.dp)
                    .width(150.dp),

                ) {
                Text(text = "Back")
            }
            Button(
                onClick = { verifyViewModel.verifyPhone(phone, code.value) },
                modifier = Modifier
                    .testTag("loginVerifyNextButton")
                    .padding(top = 100.dp)
                    .width(150.dp)
                ) {
                Text(text = "Next")
            }
        }
    }
}