package android.rapt.chat.viewmodels

import android.rapt.chat.common.RaptConstants
import android.rapt.chat.models.LoginRequest
import android.rapt.chat.models.LoginResponse
import android.rapt.chat.repositories.AuthRepository
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
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
                val loginRequest = LoginRequest(
                    phone = phone,
                    clientId = RaptConstants.CLIENT_APP_ID,
                    clientSecret = RaptConstants.CLIENT_APP_SECRET
                )
                val loginResponse: LoginResponse = authRepository.login(
                    loginRequest
                )
                _loginState.update {
                    it.copy(loginResponse = loginResponse, isLoading = false, error = null)
                }
            } catch (e: HttpException) {
                val error = "Login HttpException: ${e.response()} ${e.localizedMessage}"
                _loginState.update {
                    it.copy(loginResponse = null, isLoading = false, error = error)
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
