package rapt.chat.raptandroid.presentation.chats

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import rapt.chat.raptandroid.data.model.Auth
import rapt.chat.raptandroid.data.model.ChatRoom
import rapt.chat.raptandroid.data.repository.AuthRepository
import rapt.chat.raptandroid.data.repository.ChatsRepository
import retrofit2.HttpException
import java.io.IOException
import javax.inject.Inject

data class ChatRoomsState(
    val isLoading: Boolean = false,
    val chatRooms: List<ChatRoom> = emptyList(),
    val error: String? = null,
    val currentUser: Auth? = null
)

@HiltViewModel
class ChatsViewModel @Inject constructor(
    private val chatsRepository: ChatsRepository,
    private val authRepository: AuthRepository
): ViewModel() {
    private val _state = MutableStateFlow(ChatRoomsState())
    val state: StateFlow<ChatRoomsState> = _state.asStateFlow()

    fun setUpChatRooms(){
        viewModelScope.launch {
            try {
                _state.update {
                    it.copy(isLoading = true)
                }
                val chatRooms = chatsRepository.getChatRooms()
                println("ChatRooms: $chatRooms")
                val chatRoomsSockets = chatsRepository.connectToChatRooms(chatRooms)
                println("ChatRoomsSockets: $chatRoomsSockets")
                val currentUser = authRepository.auth()
                println("CurrentUser: $currentUser")
                _state.update {
                    it.copy(chatRooms = chatRooms, isLoading = false, error = null, currentUser = currentUser)
                }
            } catch (e: HttpException) {
                val error = "ChatRooms HttpException: ${e.response()} ${e.localizedMessage}"
                println(error)
                _state.update {
                    it.copy(chatRooms = emptyList(), isLoading = false, error = error)
                }
            } catch (e: IOException) {
                val error = "ChatRooms IOException: ${e.localizedMessage ?: "Couldn't reach server. Check your internet connection"}"
                println(error)
                _state.update {
                    it.copy(chatRooms = emptyList(), isLoading = false, error = error)
                }
            } catch (e: java.lang.SecurityException) {
                val error = "ChatRooms SecurityException: ${e.localizedMessage ?: "Unexpected error"}"
                println(error)
                _state.update {
                    it.copy(chatRooms = emptyList(), isLoading = false, error = error)
                }
            }
        }

    }

}