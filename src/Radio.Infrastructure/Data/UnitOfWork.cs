using Google.Cloud.Firestore;

namespace Radio.Infrastructure.Data;

public class UnitOfWork(FirestoreDb firestoreDb) : IFirestoreUnitOfWork
{
    private readonly List<Func<WriteBatch, Task>> _pendingOperations = [];
    private bool _inTransaction;

    public List<Func<WriteBatch, Task>> PendingOperations => _pendingOperations;

    public Task BeginTransactionAsync(CancellationToken cancellationToken = default)
    {
        _pendingOperations.Clear();
        _inTransaction = true;
        return Task.CompletedTask;
    }

    public async Task CommitTransactionAsync(CancellationToken cancellationToken = default)
    {
        if (!_inTransaction) return;
        _inTransaction = false;

        if (_pendingOperations.Any())
        {
            WriteBatch batch = firestoreDb.StartBatch();
            foreach (Func<WriteBatch, Task> op in _pendingOperations)
            {
                await op(batch);
            }
            await batch.CommitAsync(cancellationToken);
            _pendingOperations.Clear();
        }
    }

    public Task RollbackTransactionAsync(CancellationToken cancellationToken = default)
    {
        _inTransaction = false;
        _pendingOperations.Clear();
        return Task.CompletedTask;
    }

    public async Task<int> SaveChangesAsync(CancellationToken cancellationToken = default)
    {
        // SaveChanges is only executed if we are NOT in an active transaction
        // (if we are in a transaction, operations stay pending until CommitTransactionAsync is called)
        if (_pendingOperations.Count > 0 && !_inTransaction)
        {
            WriteBatch batch = firestoreDb.StartBatch();
            foreach (Func<WriteBatch, Task> op in _pendingOperations)
            {
                await op(batch);
            }
            await batch.CommitAsync(cancellationToken);
            int count = _pendingOperations.Count;
            _pendingOperations.Clear();
            return count;
        }
        return 0;
    }

    public void Dispose()
    {
        _inTransaction = false;
        _pendingOperations.Clear();
    }
}
