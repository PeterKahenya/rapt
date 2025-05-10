package android.rapt.chat.viewmodels

import android.rapt.chat.models.ProfileUpdateRequest
import android.rapt.chat.models.User
import android.rapt.chat.repositories.ProfileRepository
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.google.gson.Gson
import com.google.gson.JsonSyntaxException
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import retrofit2.HttpException
import java.io.IOException
import javax.inject.Inject

data class ProfileState(
    val isLoading: Boolean = false,
    val user: User? = null,
    val error: String? = null
)

@HiltViewModel
class ProfileViewModel @Inject constructor(
    private val profileRepository: ProfileRepository
) : ViewModel(){

    private val _profileState = MutableStateFlow(ProfileState())
    val profileState: StateFlow<ProfileState> = _profileState.asStateFlow()

    init {
        getProfile()
    }

    fun getProfile() {
        viewModelScope.launch {
            try {
                _profileState.update {
                    it.copy(isLoading = true)
                }
                val userProfile: User = profileRepository.getProfile()
                _profileState.update {
                    it.copy(user = userProfile, isLoading = false, error = null)
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
                _profileState.update {
                    it.copy(user = null, isLoading = false, error = errorResponse?.detail?.message)
                }
            } catch (e: IOException) {
                val error = "GetProfile IOException: ${e.localizedMessage ?: "Couldn't reach server. Check your internet connection"}"
                _profileState.update {
                    it.copy(user = null, isLoading = false, error = error)
                }
            } catch (e: java.lang.SecurityException) {
                val error = "GetProfile SecurityException: ${e.localizedMessage ?: "Unexpected error"}"
                _profileState.update {
                    it.copy(user = null, isLoading = false, error = error)
                }
            }
        }
    }

    fun updateProfile(userId: String, name: String?, deviceFcmToken: String?){
        viewModelScope.launch {
            try {
                _profileState.update {
                    it.copy(isLoading = true)
                }
                val profileUpdateResponse: User = profileRepository.updateProfile(userId,ProfileUpdateRequest(
                    name = name,
                    deviceFcmToken = deviceFcmToken
                ))
                _profileState.update {
                    it.copy(user = profileUpdateResponse, isLoading = false, error = null)
                }
            } catch (e: HttpException) {
                val error = "UpdateProfile HttpException: ${e.response()} ${e.localizedMessage}"
                _profileState.update {
                    it.copy(user = null, isLoading = false, error = error)
                }
            } catch (e: IOException) {
                val error = "UpdateProfile IOException: ${e.localizedMessage ?: "Couldn't reach server. Check your internet connection"}"
                _profileState.update {
                    it.copy(user = null, isLoading = false, error = error)
                }
            } catch (e: java.lang.SecurityException) {
                val error = "UpdateProfile SecurityException: ${e.localizedMessage ?: "Unexpected error"}"
                _profileState.update {
                    it.copy(user = null, isLoading = false, error = error)
                }
            }
        }
    }
}