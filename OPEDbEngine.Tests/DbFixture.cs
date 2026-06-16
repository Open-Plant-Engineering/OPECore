[assembly: CollectionBehavior(DisableTestParallelization = true)]

public class DbFixture : IAsyncLifetime
{
    public async Task InitializeAsync()
    {
        await TestDbFactory.ResetAsync();
    }

    public Task DisposeAsync() => Task.CompletedTask;
}