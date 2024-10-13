package rapt.chat.raptandroid.presentation.welcome

import android.util.Log
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import rapt.chat.raptandroid.data.repository.AuthRepository
import javax.inject.Inject

data class AuthState(
    val isLoading: Boolean = false,
    val isAuthenticated: Boolean = false,
    val error: String? = null
)

@HiltViewModel
class WelcomeViewModel @Inject constructor(
    val authRepository: AuthRepository
) : ViewModel() {
    private val _isAuthenticated = MutableStateFlow(AuthState())
    val isAuthenticated: StateFlow<AuthState> = _isAuthenticated.asStateFlow()

    init {
        Log.i("WelcomeViewModel", "init")
        checkAuth()
    }

    private fun checkAuth(){
        Log.i("WelcomeViewModel", "checkAuth")
        viewModelScope.launch {
            try {
                _isAuthenticated.update {
                    it.copy(isLoading = true, isAuthenticated = false, error = null)
                }
                val auth = authRepository.auth()
                Log.d("WelcomeViewModel", "checkAuth: auth: $auth")
                if (auth != null) {
                    _isAuthenticated.update {
                        it.copy(isAuthenticated = true, isLoading = false, error = null)
                    }
                } else {
                    _isAuthenticated.update {
                        it.copy(isAuthenticated = false, isLoading = false, error = null)
                    }
                }
            } catch (e: Exception) {
                Log.e("WelcomeViewModel", "checkAuth: ${e.localizedMessage}")
                _isAuthenticated.update {
                    it.copy(isAuthenticated = false, isLoading = false, error = e.localizedMessage)
                }
            }
        }
    }
}