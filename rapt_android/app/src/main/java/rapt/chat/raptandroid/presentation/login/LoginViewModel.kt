package rapt.chat.raptandroid.presentation.login

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import rapt.chat.raptandroid.common.Constants
import rapt.chat.raptandroid.data.model.LoginResponse
import rapt.chat.raptandroid.data.repository.AuthRepository
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
    private val authRepository: AuthRepository,
): ViewModel() {
    private val _state = MutableStateFlow(LoginState())
    val state: StateFlow<LoginState> = _state.asStateFlow()

    fun login(phone: String){
        viewModelScope.launch {
            try {
                _state.update {
                    it.copy(isLoading = true)
                }
                val loginResponse: LoginResponse = authRepository.login(
                    phone = phone,
                    clientId = Constants.CLIENT_APP_ID,
                    clientSecret = Constants.CLIENT_APP_SECRET
                )
                println("LoginResponse: $loginResponse")
                _state.update {
                    it.copy(loginResponse = loginResponse, isLoading = false, error = null)
                }
            } catch (e: HttpException) {
                val error = "Login HttpException: ${e.response()} ${e.localizedMessage}"
                println(error)
                _state.update {
                    it.copy(loginResponse = null, isLoading = false, error = error)
                }
            } catch (e: IOException) {
                val error = "Login IOException: ${e.localizedMessage ?: "Couldn't reach server. Check your internet connection"}"
                println(error)
                _state.update {
                    it.copy(loginResponse = null, isLoading = false, error = error)
                }
            }catch (e: java.lang.SecurityException){
                val error = "Login SecurityException: ${e.localizedMessage ?: "Unexpected error"}"
                println(error)
                _state.update {
                    it.copy(loginResponse = null, isLoading = false, error = error)
                }
            }
        }
    }
}