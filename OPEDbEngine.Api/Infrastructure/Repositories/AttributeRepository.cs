using Dapper;
using OPEDbEngine.Infrastructure.Models;
using OPEDbEngine.Infrastructure.Sql;
using OPEDbEngine.Core.Interfaces;
using System.Data;
using OPEDbEngine.Core.Models;

namespace OPEDbEngine.Infrastructure.Repositories
{
    public class AttributeRepository
    {
        public async Task<List<AttributeSetItemRow>> GetBySetId(
            IDbConnection conn,
            Guid setId,
            IDbTransaction? tx = null)
        {
            var result = await conn.QueryAsync<AttributeSetItemRow>(
                AttributeSql.GetItemsBySetId,
                new { SetId = setId },
                tx);

            return result.ToList();
        }

        public async Task<Guid?> GetSetIdByHash(
            IDbConnection conn,
            byte[] hash,
            IDbTransaction tx)
        {
            return await conn.ExecuteScalarAsync<Guid?>(
                AttributeSql.GetSetByHash,
                new { Hash = hash },
                tx);
        }

        public async Task InsertAttributeSet(
            IDbConnection conn,
            Guid setId,
            byte[] hash,
            IDbTransaction tx)
        {
            await conn.ExecuteAsync(
                AttributeSql.InsertAttributeSet,
                new { Id = setId, Hash = hash },
                tx);
        }

        public async Task InsertItems(
            IDbConnection conn,
            Guid setId,
            IEnumerable<AttributeItem> items,
            IDbTransaction tx)
        {
            foreach (var item in items)
            {
                await conn.ExecuteAsync(
                    AttributeSql.InsertAttributeItem,
                    new
                    {
                        SetId = setId,
                        item.Key,
                        item.ValueHash,
                        item.ValueType
                    },
                    tx);
            }
        }

        public async Task<Guid?> GetEmptySet(
            IDbConnection conn,
            IDbTransaction tx)
        {
            return await conn.ExecuteScalarAsync<Guid?>(
                AttributeSql.GetEmptySet,
                transaction: tx);
        }
    }
}