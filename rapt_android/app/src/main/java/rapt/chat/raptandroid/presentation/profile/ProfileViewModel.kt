package rapt.chat.raptandroid.presentation.profile

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import rapt.chat.raptandroid.data.model.ProfileResponse
import rapt.chat.raptandroid.data.model.ProfileUpdateRequest
import rapt.chat.raptandroid.data.repository.ProfileRepository
import retrofit2.HttpException
import java.io.IOException
import javax.inject.Inject

data class ProfileState(
    val isLoading: Boolean = false,
    val profileResponse: ProfileResponse? = null,
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
                val getProfileResponse: ProfileResponse = profileRepository.getProfile()
                println("VerifyPhoneResponse: $getProfileResponse")
                _profileState.update {
                    it.copy(profileResponse = getProfileResponse, isLoading = false, error = null)
                }
            } catch (e: HttpException) {
                val error = "GetProfile HttpException: ${e.response()} ${e.localizedMessage}"
                println(error)
                _profileState.update {
                    it.copy(profileResponse = null, isLoading = false, error = error)
                }
            } catch (e: IOException) {
                val error = "GetProfile IOException: ${e.localizedMessage ?: "Couldn't reach server. Check your internet connection"}"
                println(error)
                _profileState.update {
                    it.copy(profileResponse = null, isLoading = false, error = error)
                }
            } catch (e: java.lang.SecurityException) {
                val error = "GetProfile SecurityException: ${e.localizedMessage ?: "Unexpected error"}"
                println(error)
                _profileState.update {
                    it.copy(profileResponse = null, isLoading = false, error = error)
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
                println("ProfileUpdate: $userId $name $deviceFcmToken")
                val profileUpdateRequest = ProfileUpdateRequest(
                    name = name,
                    deviceFcmToken = deviceFcmToken
                )
                val profileUpdateResponse: ProfileResponse = profileRepository.updateProfile(userId,profileUpdateRequest)
                println("ProfileUpdateResponse: $profileUpdateResponse")
                _profileState.update {
                    it.copy(profileResponse = profileUpdateResponse, isLoading = false, error = null)
                }
            } catch (e: HttpException) {
                val error = "UpdateProfile HttpException: ${e.response()} ${e.localizedMessage}"
                println(error)
                _profileState.update {
                    it.copy(profileResponse = null, isLoading = false, error = error)
                }
            } catch (e: IOException) {
                val error = "UpdateProfile IOException: ${e.localizedMessage ?: "Couldn't reach server. Check your internet connection"}"
                println(error)
                _profileState.update {
                    it.copy(profileResponse = null, isLoading = false, error = error)
                }
            } catch (e: java.lang.SecurityException) {
                val error = "UpdateProfile SecurityException: ${e.localizedMessage ?: "Unexpected error"}"
                println(error)
                _profileState.update {
                    it.copy(profileResponse = null, isLoading = false, error = error)
                }
            }
        }
    }
}