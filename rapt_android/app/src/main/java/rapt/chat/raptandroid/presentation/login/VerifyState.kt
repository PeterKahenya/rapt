package rapt.chat.raptandroid.presentation.login

import rapt.chat.raptandroid.data.model.VerifyResponse

data class VerifyState(
    val isLoading: Boolean = false,
    val verifyResponse: VerifyResponse? = null,
    val error: String = ""
)
