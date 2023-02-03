using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace CamerAi.API.Migrations
{
    public partial class detectionlat : Migration
    {
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<double>(
                name: "Latitude",
                table: "Detections",
                type: "float",
                nullable: true);

            migrationBuilder.AddColumn<double>(
                name: "Longitude",
                table: "Detections",
                type: "float",
                nullable: true);
        }

        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropColumn(
                name: "Latitude",
                table: "Detections");

            migrationBuilder.DropColumn(
                name: "Longitude",
                table: "Detections");
        }
    }
}
