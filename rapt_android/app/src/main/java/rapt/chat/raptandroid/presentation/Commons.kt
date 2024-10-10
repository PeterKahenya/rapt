package rapt.chat.raptandroid.presentation

import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp

@Composable
fun ErrorText(text: String) {
    Text(
        text = text,
        color = Color.Red,
        modifier = Modifier.padding(vertical = 4.dp)
    )
}

@Composable
fun LoadingIndicator() {
    CircularProgressIndicator(modifier = Modifier.size(13.dp))
}