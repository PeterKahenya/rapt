package rapt.chat.raptandroid.presentation.contacts

import android.content.Context
import android.provider.ContactsContract
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import rapt.chat.raptandroid.data.model.Contact
import rapt.chat.raptandroid.data.model.ProfileUpdateRequest
import rapt.chat.raptandroid.data.repository.ProfileRepository
import javax.inject.Inject

@HiltViewModel
class ContactsViewModel @Inject constructor(
    @ApplicationContext private val context: Context,
    private val profileRepository: ProfileRepository
) : ViewModel(){

    private val _contacts = MutableStateFlow<List<Contact>>(emptyList())
    val contacts: StateFlow<List<Contact>> = _contacts

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading

    private val _error = MutableStateFlow<String?>(null)
    val error: StateFlow<String?> = _error

    init {
        loadContacts()
        uploadContacts()
    }

    private fun loadContacts() {
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null
            try {
                _contacts.value = fetchLocalContacts()
            } catch (e: Exception) {
                _error.value = "Failed to load contacts: ${e.localizedMessage}"
            } finally {
                _isLoading.value = false
            }
        }
    }

    private fun uploadContacts() {
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null
            try {
                val profile = profileRepository.getProfile()
                println("profile2: $profile")
                val contacts = fetchLocalContacts()
                val profileUpdateRequest = ProfileUpdateRequest(
                    contacts = contacts
                )
                println("profileUpdateRequest: $profileUpdateRequest")
                val updatedProfile = profileRepository.updateProfile(profile.id,profileUpdateRequest)
                println("updatedProfile: $updatedProfile")
                _contacts.value = updatedProfile.contacts
            } catch (e: Exception) {
                println("Failed to load contacts: ${e.localizedMessage}")
                _error.value = "Failed to load contacts: ${e.localizedMessage}"
            } finally {
                _isLoading.value = false
            }
        }
    }



    private suspend fun fetchLocalContacts(): List<Contact> {
            val contactsList = mutableListOf<Contact>()
            val projection = arrayOf(
                ContactsContract.CommonDataKinds.Phone.CONTACT_ID,
                ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME,
                ContactsContract.CommonDataKinds.Phone.NUMBER
            )
            context.contentResolver.query(
                ContactsContract.CommonDataKinds.Phone.CONTENT_URI,
                projection,
                null,
                null,
                ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME + " ASC"
            )?.use { cursor ->
                val idIndex = cursor.getColumnIndex(ContactsContract.CommonDataKinds.Phone.CONTACT_ID)
                val nameIndex = cursor.getColumnIndex(ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME)
                val numberIndex = cursor.getColumnIndex(ContactsContract.CommonDataKinds.Phone.NUMBER)
                if (idIndex != -1 && nameIndex != -1 && numberIndex != -1) {
                    while (cursor.moveToNext()) {
                        val id = cursor.getString(idIndex)
                        val name = cursor.getString(nameIndex)
                        val number = cursor.getString(numberIndex)
                        contactsList.add(Contact(null,phone = number.filterNot { it.isWhitespace() }, name = name))
                    }
                }
            }
            return contactsList
    }
}