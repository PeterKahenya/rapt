package android.rapt.chat

import android.os.Bundle
import android.rapt.chat.screens.VerifyScreen
import android.rapt.chat.ui.theme.RaptTheme
import android.rapt.chat.viewmodels.VerifyViewModel
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.hilt.navigation.compose.hiltViewModel
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class VerifyActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            RaptTheme {
                val viewModel = hiltViewModel<VerifyViewModel>()
                val phone = intent.getStringExtra("phone") ?: ""
                VerifyScreen(verifyViewModel = viewModel, phone = phone)
            }
        }
    }
}