package rapt.chat.raptandroid

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.hilt.navigation.compose.hiltViewModel
import dagger.hilt.android.AndroidEntryPoint
import rapt.chat.raptandroid.presentation.ui.RaptTheme
import rapt.chat.raptandroid.presentation.welcome.WelcomeScreen
import rapt.chat.raptandroid.presentation.welcome.WelcomeViewModel


@AndroidEntryPoint
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            RaptTheme {
                val viewModel = hiltViewModel<WelcomeViewModel>()
                WelcomeScreen(viewModel)
            }
        }
    }
}