package android.rapt.chat.repositories

import android.rapt.chat.models.ContactUpload
import android.rapt.chat.sources.ContactDao
import android.rapt.chat.sources.DBContact
import android.rapt.chat.sources.RaptAPI
import android.rapt.chat.sources.RaptContentProvider
import android.util.Log
import javax.inject.Inject

interface ContactsRepository {
    suspend fun sync(): List<DBContact>
    suspend fun searchContacts(query: String): List<DBContact>
    suspend fun deleteContact(contact: DBContact)
}

class ContactsRepositoryImpl @Inject constructor(
    private val api: RaptAPI,
    private val contactDB: ContactDao,
    private val contentProvider: RaptContentProvider,
    private val authRepository: AuthRepository
) : ContactsRepository {
    override suspend fun sync(): List<DBContact> {
        try {
            val auth = authRepository.auth() ?: throw Exception("No auth found")
            // upload contacts to api that are in phone but not in api
            val phoneContacts = contentProvider.getContacts()
            val apiContacts = api.getContacts(accessToken = "Bearer ${auth.accessToken}", userId = auth.userId)
            val apiUploadList = mutableListOf<ContactUpload>()
            for (phoneContact in phoneContacts){
                if (phoneContact.phone !in apiContacts.map { it.phone }){
                    apiUploadList.add(ContactUpload(name = phoneContact.name, phone = phoneContact.phone))
                }
            }
            val updatedAPIContacts = api.addContacts(
                accessToken = "Bearer ${auth.accessToken}",
                userId = auth.userId,
                addContactsRequest = apiUploadList
            )
            // any contact not in the db should be added
            val dbContacts = contactDB.getAll()
            for (apiContact in updatedAPIContacts) {
                if (apiContact.phone !in dbContacts.map { it.phone }) {
                    contactDB.insert(
                        DBContact(
                            name = apiContact.name,
                            phone = apiContact.phone,
                            contactId = apiContact.contactId,
                            userId = auth.userId,
                            isActive = apiContact.isActive
                        )
                    )
                }
            }
            return contactDB.getAll()
        } catch (ex: Exception){
            Log.d("ContactsRepositoryImpl sync", "Error syncing contacts $ex")
            return contactDB.getAll()
        }
    }

    override suspend fun searchContacts(query: String): List<DBContact> {
        return contactDB.search(query)
    }

    override suspend fun deleteContact(contact: DBContact) {
        // TODO: delete contact from api as well
        contactDB.delete(contact)
    }

}