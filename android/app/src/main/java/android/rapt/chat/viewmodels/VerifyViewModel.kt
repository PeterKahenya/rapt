package android.rapt.chat.viewmodels

import android.rapt.chat.common.RaptConstants
import android.rapt.chat.models.VerifyRequest
import android.rapt.chat.models.VerifyResponse
import android.rapt.chat.repositories.AuthRepository
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

data class VerifyState(
    val isLoading: Boolean = false,
    val verifyResponse: VerifyResponse? = null,
    val error: String? = null
)

@HiltViewModel
class VerifyViewModel @Inject constructor(
    private val authRepository: AuthRepository
): ViewModel() {
    private val _state = MutableStateFlow(VerifyState())
    val state: StateFlow<VerifyState> = _state.asStateFlow()

    fun verifyPhone(phone: String, code: String){
        viewModelScope.launch {
            try {
                _state.update {
                    it.copy(isLoading = true)
                }
                val verifyResponse: VerifyResponse = authRepository.verify(
                    VerifyRequest(
                        phoneVerificationCode = code,
                        phone = phone,
                        clientId = RaptConstants.CLIENT_APP_ID,
                        clientSecret = RaptConstants.CLIENT_APP_SECRET
                    )
                )
                _state.update {
                    it.copy(verifyResponse = verifyResponse, isLoading = false, error = null)
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
                    it.copy(verifyResponse = null, isLoading = false, error = errorResponse?.detail?.message)
                }
            } catch (e: IOException) {
                val error = "Verify IOException: ${e.localizedMessage ?: "Couldn't reach server. Check your internet connection"}"
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