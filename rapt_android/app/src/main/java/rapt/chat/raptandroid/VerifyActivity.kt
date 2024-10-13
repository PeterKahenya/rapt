package rapt.chat.raptandroid

import android.os.Bundle
import android.util.Log
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.hilt.navigation.compose.hiltViewModel
import dagger.hilt.android.AndroidEntryPoint
import rapt.chat.raptandroid.presentation.verify.VerifyViewModel
import rapt.chat.raptandroid.presentation.verify.VerifyScreen
import rapt.chat.raptandroid.presentation.ui.RaptTheme

@AndroidEntryPoint
class VerifyActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        val phone = intent.getStringExtra("phone")
        Log.i("VerifyActivity","Phone Number: $phone")
        setContent {
            RaptTheme {
                val viewModel = hiltViewModel<VerifyViewModel>()
                if (phone != null) {
                    VerifyScreen(viewModel, phone)
                }
            }
        }
    }
}
