package rapt.chat.raptandroid.presentation.login

import androidx.compose.runtime.State
import androidx.compose.runtime.mutableStateOf
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.launchIn
import kotlinx.coroutines.flow.onEach
import rapt.chat.raptandroid.common.Constants
import rapt.chat.raptandroid.common.Resource
import rapt.chat.raptandroid.data.model.VerifyRequest
import rapt.chat.raptandroid.domain.use_case.VerifyPhoneUseCase
import javax.inject.Inject

class VerifyViewModel @Inject constructor(
    private val verifyPhoneUseCase: VerifyPhoneUseCase
): ViewModel(){
    private val _state = MutableStateFlow(VerifyState())
    val state: StateFlow<VerifyState> = _state.asStateFlow()

    fun verifyPhone(phone: String, code: String){
        val verifyRequest = VerifyRequest(
            phone = phone,
            phoneVerificationCode = code,
            clientId = Constants.CLIENT_APP_ID,
            clientSecret = Constants.CLIENT_APP_SECRET
        )
        verifyPhoneUseCase(verifyRequest).onEach { result ->
            when (result) {
                is Resource.Success -> {
                    _state.value = VerifyState(verifyResponse = result.data)
                }
                is Resource.Error -> {
                    _state.value = VerifyState(error = result.message ?: "An unexpected error occurred")
                }
                is Resource.Loading -> {
                    _state.value = VerifyState(isLoading = true)
                }
            }
        }.launchIn(viewModelScope)
    }

}