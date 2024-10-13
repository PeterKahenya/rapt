package rapt.chat.raptandroid.presentation.chats

import android.util.Log
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
import rapt.chat.raptandroid.data.repository.ChatRoomSocket
import rapt.chat.raptandroid.data.repository.ChatRoomsRepository
import rapt.chat.raptandroid.data.repository.DisplayChatRoom
import rapt.chat.raptandroid.data.source.ChatRoom
import retrofit2.HttpException
import java.io.IOException
import javax.inject.Inject

data class ChatRoomsState(
    val isLoading: Boolean = false,
    val chatRooms: List<DisplayChatRoom> = emptyList(),
    val chatRoomsSockets: List<ChatRoomSocket> = emptyList(),
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
                Log.d("ChatsViewModel: ","setUpChatRooms CurrentUser: $currentUser")
                _state.update {
                    it.copy(currentUser = currentUser, error = null)
                }

                val dbChatRooms = chatRoomsRepository.getAllDBChatRooms()
                Log.d("ChatsViewModel: ","setUpChatRooms dbChatRooms: ${dbChatRooms.size}")
                _state.update {
                    it.copy(chatRooms = dbChatRooms, error = null)
                }

                val apiChatRooms = chatRoomsRepository.getAllAPIChatRooms()
                Log.d("ChatsViewModel: ","setUpChatRooms apiChatRooms: ${apiChatRooms.size}")
                for (apiChatRoom in apiChatRooms){
                    println("ApiChatRoom: MembersCount: ${apiChatRoom.members.size} ChatsCount: ${apiChatRoom.roomChats.size}")
                    chatRoomsRepository.saveChatRoom(apiChatRoom)
                }

                val dbChatRoomsUpdated = chatRoomsRepository.getAllDBChatRooms()
                println("DBChatRoomsUpdated: ${dbChatRoomsUpdated.size}")
                _state.update {
                    it.copy(chatRooms = dbChatRoomsUpdated, isLoading = false, error = null)
                }
                val chatRooms = dbChatRoomsUpdated.map { chatRoom -> ChatRoom(chatRoomId = chatRoom.roomId) }
//                val chatRoomsSockets = chatRoomsRepository.connectToChatRooms(chatRooms)
                _state.update {
                    it.copy(isLoading = false, error = null)
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