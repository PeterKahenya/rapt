package rapt.chat.raptandroid

import android.os.Bundle
import android.util.Log
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.hilt.navigation.compose.hiltViewModel
import dagger.hilt.android.AndroidEntryPoint
import rapt.chat.raptandroid.presentation.contacts.ContactsScreen
import rapt.chat.raptandroid.presentation.contacts.ContactsViewModel
import rapt.chat.raptandroid.presentation.ui.RaptTheme

@AndroidEntryPoint
class ContactsActivity : ComponentActivity(){
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        Log.i("ContactsActivity", "onCreate")
        setContent {
            RaptTheme {
                val viewModel = hiltViewModel<ContactsViewModel>()
                ContactsScreen(viewModel)
            }
        }
    }
}



