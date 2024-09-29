package rapt.chat.raptandroid.presentation.login

import androidx.compose.runtime.State
import androidx.compose.runtime.mutableStateOf
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.launchIn
import kotlinx.coroutines.flow.onEach
import rapt.chat.raptandroid.common.Constants
import rapt.chat.raptandroid.common.Resource
import rapt.chat.raptandroid.data.model.LoginRequest
import rapt.chat.raptandroid.domain.use_case.LoginUseCase
import javax.inject.Inject

@HiltViewModel
class LoginViewModel @Inject constructor(
    private val loginUseCase: LoginUseCase
): ViewModel() {
    private val _state = MutableStateFlow(LoginState())
    val state: StateFlow<LoginState> = _state.asStateFlow()

    fun login(phone: String){
        val loginRequest = LoginRequest(
            phone = phone,
            clientId = Constants.CLIENT_APP_ID,
            clientSecret = Constants.CLIENT_APP_SECRET
        )
        loginUseCase(loginRequest).onEach { result ->
            when (result) {
                is Resource.Success -> {
                    _state.value = LoginState(loginResponse = result.data)
                }
                is Resource.Error -> {
                    _state.value = LoginState(error = result.message ?: "An unexpected error occurred")
                }
                is Resource.Loading -> {
                    _state.value = LoginState(isLoading = true)
                }
            }
        }.launchIn(viewModelScope)
    }
}