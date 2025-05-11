package android.rapt.chat.viewmodels

import android.rapt.chat.repositories.ChatsRepository
import android.rapt.chat.sources.DBChatRoomWithMembersAndMessages
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.google.gson.Gson
import com.google.gson.JsonSyntaxException
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import retrofit2.HttpException
import javax.inject.Inject

data class ChatsListState(
    var rooms: List<DBChatRoomWithMembersAndMessages> = emptyList(),
    var isLoading: Boolean = false,
    var error: String? = null
)

@HiltViewModel
class ChatsListViewModel @Inject constructor(
    private val chatsRepository: ChatsRepository
) : ViewModel() {
    private val _state = MutableStateFlow(ChatsListState())
    val state = _state.asStateFlow()

    init {
        syncChatRooms()
    }

    private fun syncChatRooms() {
        viewModelScope.launch {
            try {
                _state.update {
                    it.copy(isLoading = true, error = null)
                }
                val dbChatRooms = chatsRepository.sync()
                _state.update {
                    it.copy(rooms = dbChatRooms, isLoading = false, error = null)
                }
            } catch (e: HttpException) {
                val errorResponse: ErrorResponse?
                if (e.code() == 400 || e.code() == 401) {
                    val errorBody = e.response()?.errorBody()?.string()
                    errorResponse = try {
                        Gson().fromJson(errorBody, ErrorResponse::class.java)
                    } catch (e: JsonSyntaxException) {
                        null
                    }
                    if (errorResponse != null) {
                        errorResponse.statusCode = e.code()
                    }
                } else {
                    errorResponse = ErrorResponse(
                        detail = ErrorDetails(message = e.message()),
                        statusCode = e.code()
                    )
                }
                _state.update {
                    it.copy(isLoading = false, error = errorResponse?.detail?.message)
                }
            } catch (e: Exception) {
                _state.update {
                    it.copy(isLoading = false, error = e.localizedMessage)
                }
            } finally {
                _state.update {
                    it.copy(isLoading = false, error = null)
                }
            }
        }
    }
}