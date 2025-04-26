package android.rapt.chat

import android.os.Bundle
import android.rapt.chat.screens.LoginScreen
import android.rapt.chat.theme.RaptTheme
import android.rapt.chat.viewmodels.LoginViewModel
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.hilt.navigation.compose.hiltViewModel
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class LoginActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            RaptTheme {
                val viewModel: LoginViewModel = hiltViewModel<LoginViewModel>()
                LoginScreen(viewModel)
            }
        }
    }
}