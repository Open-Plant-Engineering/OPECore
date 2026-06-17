using Dapper;
using OPEDbEngine.Infrastructure.Models;
using OPEDbEngine.Infrastructure.Sql;
using OPEDbEngine.Core.Interfaces;
using System.Data;

namespace OPEDbEngine.Infrastructure.Repositories
{
    public class AttributeRepository
    {
        public async Task<List<AttributeSetItemRow>> GetBySetId(
            IDbConnection conn,
            Guid setId,
            IDbTransaction tx)
        {
            var result = await conn.QueryAsync<AttributeSetItemRow>(
                AttributeSql.GetItemsBySetId,
                new { SetId = setId },
                tx);

            return result.ToList();
        }
    }
}