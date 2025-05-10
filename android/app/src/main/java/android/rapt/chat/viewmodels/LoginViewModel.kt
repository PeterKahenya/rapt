package android.rapt.chat.viewmodels

import android.rapt.chat.common.RaptConstants
import android.rapt.chat.models.LoginRequest
import android.rapt.chat.models.LoginResponse
import android.rapt.chat.repositories.AuthRepository
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.google.gson.Gson
import com.google.gson.JsonSyntaxException
import com.google.gson.annotations.SerializedName
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import retrofit2.HttpException
import java.io.IOException
import javax.inject.Inject

data class LoginState(
    val isLoading: Boolean = false,
    val loginResponse: LoginResponse? = null,
    val error: String? = null
)
data class ErrorDetails(
    @SerializedName("message") val message: String? = null,
)
data class ErrorResponse(
    @SerializedName("detail") val detail: ErrorDetails? = null,
    @SerializedName("statusCode") var statusCode: Int? = null
)

@HiltViewModel
class LoginViewModel @Inject constructor(
    private val authRepository: AuthRepository
): ViewModel() {
    private val _loginState = MutableStateFlow(LoginState())
    val loginState: StateFlow<LoginState> = _loginState.asStateFlow()

    fun login(phone: String){
        viewModelScope.launch {
            try {
                _loginState.update {
                    it.copy(isLoading = true)
                }
                val loginResponse: LoginResponse = authRepository.login(
                    LoginRequest(
                        phone = phone,
                        clientId = RaptConstants.CLIENT_APP_ID,
                        clientSecret = RaptConstants.CLIENT_APP_SECRET
                    )
                )
                _loginState.update {
                    it.copy(loginResponse = loginResponse, isLoading = false, error = null)
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
                _loginState.update {
                    it.copy(loginResponse = null, isLoading = false, error = errorResponse?.detail?.message)
                }
            } catch (e: IOException) {
                val error = "Login IOException: ${e.localizedMessage ?: "Couldn't reach server. Check your internet connection"}"
                _loginState.update {
                    it.copy(loginResponse = null, isLoading = false, error = error)
                }
            }catch (e: java.lang.SecurityException){
                val error = "Login SecurityException: ${e.localizedMessage ?: "Unexpected error"}"
                _loginState.update {
                    it.copy(loginResponse = null, isLoading = false, error = error)
                }
            }
        }
    }
}
