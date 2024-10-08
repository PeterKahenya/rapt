package rapt.chat.raptandroid.presentation.contacts

import android.content.Context
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import rapt.chat.raptandroid.data.model.APIContact
import rapt.chat.raptandroid.data.repository.ContactsRepository
import rapt.chat.raptandroid.data.source.Contact
import retrofit2.HttpException
import javax.inject.Inject

data class ContactsState(
    var contacts: List<Contact> = emptyList(),
    var isLoading: Boolean = false,
    var error: String? = null
)

@HiltViewModel
class ContactsViewModel @Inject constructor(
    @ApplicationContext private val context: Context,
    private val contactsRepository: ContactsRepository
) : ViewModel(){
    private val _state = MutableStateFlow(ContactsState())
    val state = _state.asStateFlow()

    init {
        syncContacts()
    }

    private fun syncContacts() {
        viewModelScope.launch {
            try {
                _state.update {
                    it.copy(isLoading = true, error = null)
                }
                val dbContacts = contactsRepository.getAllDBContacts()
                println("dbContacts ${dbContacts.size}")
                _state.update {
                    it.copy(contacts = dbContacts, error = null)
                }
                val phoneContacts = contactsRepository.getPhoneContacts()
                println("phoneContacts $phoneContacts")
                val apiContacts = if (phoneContacts.isEmpty()){
                    contactsRepository.apiFetchContacts()
                }else{
                    contactsRepository.uploadContacts(phoneContacts)
                }
                println("API Contacts: $apiContacts")
                contactsRepository.saveContacts(apiContacts)
                println("DB Contacts Saved")
                val dbContactsUpdated = contactsRepository.getAllDBContacts()
                println("DB Contacts Updated: ${dbContactsUpdated.size}")
                _state.update {
                    it.copy(contacts = dbContactsUpdated, isLoading = false, error = null)
                }
                println("Rapt Contacts synced")
            } catch (e: HttpException) {
                println("Failed to sync contacts: ${e.response()?.errorBody()?.string()}")
                _state.value = ContactsState(error = e.localizedMessage, isLoading = false)
            } catch (e: Exception) {
                println("Failed to sync contacts: ${e.localizedMessage}")
                _state.update {
                    it.copy(error = e.localizedMessage, isLoading = false)
                }
            } finally {
                _state.update {
                    it.copy(isLoading = false, error = null)
                }
            }
        }
    }
}