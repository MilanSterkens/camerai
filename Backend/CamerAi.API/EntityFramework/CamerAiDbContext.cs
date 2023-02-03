using CamerAi.API.Models;
using CamerAi.DAL.DTOs;
using Microsoft.EntityFrameworkCore;

namespace CamerAi.API.EntityFramework;

public class CamerAiDbContext: DbContext
{
    public CamerAiDbContext(DbContextOptions<CamerAiDbContext> options) : base(options)
    { }
    public DbSet<Device> Devices { get; set; }
    public DbSet<VehicleDetection> Detections { get; set; }
    public DbSet<VehicleDeviceMaxSpeed> VehicleDeviceMaxSpeeds { get; set; }
    public DbSet<User> Users { get; set; }

}