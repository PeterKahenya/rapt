package android.rapt.chat

import android.os.Bundle
import android.rapt.chat.theme.RaptTheme
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.material3.Text

class ChatActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        val contactId = intent.getStringExtra("contactId")
        setContent {
            RaptTheme {
                Text("Chat Activity with Contact ID: $contactId")
            }
        }
    }
}