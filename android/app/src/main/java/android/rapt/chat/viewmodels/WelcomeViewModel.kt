package android.rapt.chat.viewmodels

import android.rapt.chat.repositories.AuthRepository
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

data class AuthState(
    val isLoading: Boolean = false,
    val isAuthenticated: Boolean = false,
    val error: String? = null
)

@HiltViewModel
class WelcomeViewModel @Inject constructor(
    private val authRepository: AuthRepository
): ViewModel() {

    private val _authState = MutableStateFlow(AuthState())
    val authState: StateFlow<AuthState> = _authState.asStateFlow()

    init {
        checkAuth()
    }

    private fun checkAuth(){
        viewModelScope.launch {
            try {
                _authState.update {
                    it.copy(isLoading = true, isAuthenticated = false, error = null)
                }
                val auth = authRepository.auth()
                if (auth != null) {
                    _authState.update {
                        it.copy(isAuthenticated = true, isLoading = false, error = null)
                    }
                } else {
                    _authState.update {
                        it.copy(isAuthenticated = false, isLoading = false, error = "No auth found")
                    }
                }
            } catch (e: Exception) {
                _authState.update {
                    it.copy(isAuthenticated = false, isLoading = false, error = e.localizedMessage)
                }
            }
        }
    }
}

