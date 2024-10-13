package rapt.chat.raptandroid.presentation.verify

import android.util.Log
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import rapt.chat.raptandroid.common.Constants
import rapt.chat.raptandroid.data.model.VerifyResponse
import rapt.chat.raptandroid.data.repository.AuthRepository
import retrofit2.HttpException
import java.io.IOException
import javax.inject.Inject

data class VerifyState(
    val isLoading: Boolean = false,
    val verifyResponse: VerifyResponse? = null,
    val error: String? = null
)

@HiltViewModel
class VerifyViewModel @Inject constructor(
    private val authRepository: AuthRepository
): ViewModel(){

    private val _state = MutableStateFlow(VerifyState())
    val state: StateFlow<VerifyState> = _state.asStateFlow()

    fun verifyPhone(phone: String, code: String){
        viewModelScope.launch {
            try {
                _state.update {
                    it.copy(isLoading = true)
                }
                val verifyResponse: VerifyResponse = authRepository.verify(
                    phoneVerificationCode = code,
                    phone = phone,
                    clientId = Constants.CLIENT_APP_ID,
                    clientSecret = Constants.CLIENT_APP_SECRET
                )
                Log.d("VerifyViewModel","VerifyPhoneResponse: $verifyResponse")
                _state.update {
                    it.copy(verifyResponse = verifyResponse, isLoading = false, error = null)
                }
            } catch (e: HttpException) {
                val error = "Verify HttpException: ${e.response()} ${e.localizedMessage}"
                _state.update {
                    it.copy(verifyResponse = null, isLoading = false, error = error)
                }
            } catch (e: IOException) {
                val error = "Verify IOException: ${e.localizedMessage ?: "Couldn't reach server. Check your internet connection"}"
                println(error)
                _state.update {
                    it.copy(verifyResponse = null, isLoading = false, error = error)
                }
            }catch (e: java.lang.SecurityException){
                val error = "Verify SecurityException: ${e.localizedMessage ?: "Unexpected error"}"
                _state.update {
                    it.copy(verifyResponse = null, isLoading = false, error = error)
                }
            }
        }
    }

}