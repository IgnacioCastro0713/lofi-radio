using Google.Cloud.Firestore;
using Radio.Domain.Interfaces;

namespace Radio.Infrastructure.Data;

public interface IFirestoreUnitOfWork : IUnitOfWork
{
    List<Func<WriteBatch, Task>> PendingOperations { get; }
}
