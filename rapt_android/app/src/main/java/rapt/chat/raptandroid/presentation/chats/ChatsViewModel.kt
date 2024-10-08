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
import rapt.chat.raptandroid.data.repository.AuthRepository
import rapt.chat.raptandroid.data.repository.ChatRoomsRepository
import rapt.chat.raptandroid.data.repository.DisplayChatRoom
import rapt.chat.raptandroid.data.source.ChatRoom
import retrofit2.HttpException
import java.io.IOException
import javax.inject.Inject

data class ChatRoomsState(
    val isLoading: Boolean = false,
    val chatRooms: List<DisplayChatRoom> = emptyList(),
    val error: String? = null,
    val currentUser: Auth? = null
)

@HiltViewModel
class ChatsViewModel @Inject constructor(
    private val chatRoomsRepository: ChatRoomsRepository,
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
                val currentUser = authRepository.auth()
                println("CurrentUser: $currentUser")
                _state.update {
                    it.copy(currentUser = currentUser, error = null)
                }
                val dbChatRooms = chatRoomsRepository.getAllDBChatRooms()
                println("DBChatRooms: $dbChatRooms")
                _state.update {
                    it.copy(chatRooms = dbChatRooms, error = null)
                }
                val apiChatRooms = chatRoomsRepository.getAllAPIChatRooms()
                println("ApiChatRooms: $apiChatRooms")
                for (apiChatRoom in apiChatRooms){
                    chatRoomsRepository.saveChatRoom(apiChatRoom)
                }
                val dbChatRoomsUpdated = chatRoomsRepository.getAllDBChatRooms()
                println("DBChatRoomsUpdated: $dbChatRoomsUpdated")
                _state.update {
                    it.copy(chatRooms = dbChatRoomsUpdated, isLoading = false, error = null)
                }
                val chatRooms = dbChatRoomsUpdated.map { chatRoom -> ChatRoom(chatRoomId = chatRoom.roomId) }
                chatRoomsRepository.connectToChatRooms(chatRooms)
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