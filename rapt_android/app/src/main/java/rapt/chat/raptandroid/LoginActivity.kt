package rapt.chat.raptandroid

import android.os.Bundle
import android.util.Log
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.hilt.navigation.compose.hiltViewModel
import dagger.hilt.android.AndroidEntryPoint
import rapt.chat.raptandroid.presentation.login.LoginViewModel
import rapt.chat.raptandroid.presentation.login.LoginScreen
import rapt.chat.raptandroid.presentation.ui.RaptTheme

@AndroidEntryPoint
class LoginActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        Log.i("LoginActivity", "onCreate")
        setContent {
            RaptTheme {
                    val viewModel = hiltViewModel<LoginViewModel>()
                    LoginScreen(viewModel)
                }
            }
        }
}

