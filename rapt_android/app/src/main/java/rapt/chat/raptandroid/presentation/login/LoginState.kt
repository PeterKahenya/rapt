package rapt.chat.raptandroid.presentation.login

import rapt.chat.raptandroid.data.model.LoginRequest
import rapt.chat.raptandroid.data.model.LoginResponse

data class LoginState(
    val isLoading: Boolean = false,
    val loginRequest: LoginRequest? = null,
    val loginResponse: LoginResponse? = null,
    val error: String? = null
)
