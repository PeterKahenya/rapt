package rapt.chat.raptandroid

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.hilt.navigation.compose.hiltViewModel
import dagger.hilt.android.AndroidEntryPoint
import rapt.chat.raptandroid.presentation.profile.ProfileScreen
import rapt.chat.raptandroid.presentation.profile.ProfileViewModel
import rapt.chat.raptandroid.presentation.ui.RaptTheme

@AndroidEntryPoint
class ProfileActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            RaptTheme {
                val viewModel = hiltViewModel<ProfileViewModel>()
                ProfileScreen(viewModel)
            }
        }
    }
}