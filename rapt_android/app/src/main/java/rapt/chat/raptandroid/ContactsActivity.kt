package rapt.chat.raptandroid

import android.Manifest
import android.content.pm.PackageManager
import android.os.Bundle
import android.util.Log
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.hilt.navigation.compose.hiltViewModel
import dagger.hilt.android.AndroidEntryPoint
import rapt.chat.raptandroid.presentation.contacts.ContactsScreen
import rapt.chat.raptandroid.presentation.contacts.ContactsViewModel
import rapt.chat.raptandroid.presentation.ui.RaptTheme

@AndroidEntryPoint
class ContactsActivity : ComponentActivity(){
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            RaptTheme {
                val viewModel = hiltViewModel<ContactsViewModel>()
                ContactsScreen(viewModel)
            }
        }
    }
}



